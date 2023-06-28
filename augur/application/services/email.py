from augur.tasks.init.redis_connection import redis_connection as redis
from augur.application.config import AugurConfig
from augur.application.db.models import User
from augur.api.server import db_session
from augur.api.util import generate_OTP

from flask import url_for, request

import logging, time, secrets

logger = logging.getLogger(__name__)
config = AugurConfig(logger, db_session)

def maybe_refresh_otp(user: User, seconds: int):
    """Check redis for an existing one-time passcode
    for email verification.
    
    If it exists, reset the timeout to `seconds`.
    Return the existing OTP if one exists, or None.
    """

    if otp := redis.get(user.email_otp_key):
        # Using `set` here instead of `expire` because the API
        # documentation is not super clear on what happens if
        # the expiry is reached before `expire` is used.
        redis.set(user.email_otp_key, otp, ex=seconds)
    
    return otp

def create_otp(user: User, seconds: int):
    """Create a new one-time passcode in Redis for this user's
    email verification.
    
    Sets the timeout to `seconds`, and
    returns the newly created OTP.
    """
    otp = generate_OTP()
    redis.set(user.email_otp_key, otp, ex=seconds)
    return otp

def create_or_refresh_otp(user: User, seconds: int):
    """Attempt to refresh an existing one-time passcode
    for email verification associated with this user.

    If one does not exist, a new one is created. In either
    case, the timeout will be set to `seconds`, and the OTP
    will be returned.
    """
    return maybe_refresh_otp(user, seconds) or create_otp(user, seconds)

def create_timestamp_key(user: User, seconds: int):
    """Create a new unique token with the current unix epoch
    timestamp in milliseconds embedded in the first portion
    of the bytes.
    
    Sets the timeout to `seconds`, and returns the newly
    created token.
    
    An associated user-keyed entry is set in redis so a reverse
    lookup of the generated token can be made. This entry does
    not expire."""
    ms = int(time.time() * 1000)
    prefix = hex(ms).removeprefix("0x")

    token = prefix + secrets.token_hex(12)

    redis.set(token, user.user_id, ex=seconds)
    redis.set(user.password_reset_key, token)

    return token

def maybe_refresh_timestamp_key(user: User, seconds: int):
    """Attempt to refresh an existing timestamped key
    stored in redis assocaited with this user.
    
    If it exists, reset the timeout to `seconds`.
    Return the existing timestamped key, or None.
    """
    token = redis.get(user.password_reset_key)

    # The user-keyed entry does not expire
    # If this exists, it means a request was previously made
    if token:
        UID = redis.get(token)
        if UID:
            # The token is still valid, and so is refreshed
            redis.set(token, UID, ex=seconds)
            return token
        else:
            # The request existed, but expired
            # We delete the user-keyed entry
            redis.delete(user.password_reset_key)
    
    # Explicitly return None here for readability
    return None

def create_or_refresh_timestamp_key(user: User, seconds: int):
    return maybe_refresh_timestamp_key(user, seconds) or create_timestamp_key(user, seconds)

class EmailProvider:
    def __init__(self) -> None:
        self.verification_html = """<p><strong>This One Time Passcode expires in {} minutes.</strong></p>
            <h1>{}</h1>
            <p><small>If you did not make this request, you can disregard this message.</small></p>"""
        self.verification_subject = "Augur account verification"
        self.verification_timeout_minutes = 15

        self.reset_html = """<p><strong>This reset link expires in {} minutes.</strong></p>
            <p><h1>If you did not make this request, you should immediately change your password.</h1></p>
            <strong>{}</strong>"""
        self.reset_subject = "Augur password reset"
        self.reset_timeout_minutes = 30

    def send(self, user: User, subject: str, body: str):
        """Send a message to the provided user with the given subject and body.

        Might raise an excpetion if the email provider fails to send the message.
        Exception type depends on the email provider currently enabled. Will return
        a response object if the email provider supports that functionality.
        """
        pass

    def user_verify(self, user: User)-> bool:
        """Send a verification email to the provided user, and set a unique OTP
        in redis.
        
        Will only send if the user's email is not currently verified.
        Might raise an excpetion if the email provider fails to send the message.
        Exception type depends on the email provider currently enabled. Will return
        True if the user's email is already verified, or False if the verification
        email was sent.
        """
        pass

    def user_password_reset(self, user: User)-> bool:
        """Send a password reset email to the provided user, and set a unique
        password reset key in redis.

        Will only send if the user's email is currently verified.
        Might raise an excpetion if the email provider fails to send the message.
        Exception type depends on the email provider currently enabled. Will return
        False if the user's email is not verified, otherwise True.
        """
        pass

class SendGrid(EmailProvider):
    def __init__(self) -> None:
        super().__init__()

        # Done so Augur does not rely on the sendgrid library unless SendGrid is enabled
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail

        self.api = SendGridAPIClient
        self.email = Mail

    def send(self, user: User, subject: str, body: str):
        message = self.email(
            from_email=config.get_value("email.service", "source_email"),
            to_emails=user.email,
            subject=subject,
            html_content=body
        )

        connection = self.api(config.get_value("email.service", "provider_key"))
        return connection.send(message) # Return response object

    def user_verify(self, user: User):
        if user.email_verified:
            return True
        
        otp = create_or_refresh_otp(user, self.verification_timeout_minutes * 60)

        body = self.verification_html.format(self.verification_timeout_minutes, otp)
        response = self.send(user, self.verification_subject, body)

        return False
    
    def user_password_reset(self, user: User):
        if not user.email_verified:
            return False
        
        token = create_or_refresh_timestamp_key(user, self.reset_timeout_minutes * 60)
        url = f"{request.base_url}?rk={token}"

        body = self.reset_html.format(self.reset_timeout_minutes, url)
        response = self.send(user, self.reset_subject, body)
    
def email_enabled():
    return config.get_value("service", "email")

# Basically an EmailProviderFactory, except this isn't Java :/
def get_email_provider() -> EmailProvider:
    """Get the currently active email service provider, if one exists.

    Will return an instance of the currently active email provider, or
    None if email service is not currently enabled.
    """
    if not email_enabled():
        # Email service is not enabled
        return None
    
    provider = config.get_value("email.service", "provider")

    if provider == "twilio_sendgrid":
        return SendGrid()
