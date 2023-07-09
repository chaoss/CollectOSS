# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

message = Mail(
    from_email='metrix@goggins.com',
    to_emails='gogginss@missouri.edu',
    subject='Hi, Attached is your report of recommendations provided as a part of your DEI Badge! Contained are specific suggestions you may consider for making your project more open and welcoming to newcomers from diverse backgrounds. .... etc.',
    html_content='<strong>and easy to do anywhere, even with Python</strong>')
try:
    sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
    response = sg.send(message)
    print(response.status_code)
    print(response.body)
    print(response.headers)
except Exception as e:
    print(e.message)
