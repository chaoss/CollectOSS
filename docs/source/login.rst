Augur OAuth Flow
=================

Augur implements the Oauth 2.0 specification, and each Augur instance is capable of acting as an authorization server for external applications.

Prerequisites
--------------

If your Augur instance is running behind Nginx or Apache, make sure this parameter (or its Apache equivalent) is set in your ``sites-enabled`` configuration::

    proxy_set_header X-Forwarded-Proto $scheme;

Registering a user account on the desired Augur instance is a requirement for creating a Client Application. The developer of the application must follow the below steps:

1. Navigate to the home page of the desired Augur instance.
2. Click "Login" on the navigation bar.
3. Click "Register" and fill out the account details.

Once you have registered an account, follow the below steps to create a new Client Application:

1. Click your username in the navigation bar.
2. Click "Profile".
3. Click "Applications"
4. In the create application form, fill out the application name and redirect URL
    - The redirect URL is relative to the user-agent (i.e. the user's browser), and **must** be accessible to the user-agent.
    - If you are testing an application locally, you may use ``http://127.0.0.1/`` or ``http://localho.st`` as the host for the redirect URL. The authorization server will *not* prevent redirection if the redirect url is unreachable.

Once the application has been created, note the Application ID and Client Secret, as you will need them for application authentication requests.

Authorization Flow
--------------------

The auth flow **must** be initiated by a user intent. Your application **must not** request initial authorization on the user's behalf, and **must not** automatically redirect the user to the authorization server.

Initial Request
~~~~~~~~~~~~~~~~

The authorization flow is initiated when a user clicks a link or button which redirects the user-agent (browser) to the authorization server. This request URL must be of the following format::

    https://augur.example.com/user/authorize?
        client_id=[your application ID]
        &response_type="code"
        &state=[optional value that you define]

Authorization Response
~~~~~~~~~~~~~~~~~~~~~~~~

Upon redirection, the user is presented with a verification page on the authorization server which indicates the requesting application, what information will be shared, and where the user will be redirected after authorizing. Should the user choose to approve authorization, the authorization server will redirect the user-agent to the redirect URL provided during creationg of the Client Application. The redirect request from the authorization server will be of the following format::

    https://example.com/your/redirect/url?
        code=[temporary authorization code]
        &state=[the same state (if) provided in the previous request]

The temporary authorization code provided in this response is only valid for a number of seconds, and should be considered volatile (it is one-time use, and only exists for the duration required to complete the transaction).

The Client Application **must not** store the temporary authorization code for any longer than is necessary to exchange the code for a User Session Token. The following request must be made immediately upon receipt of the temporary authorization code.

Temporary Code Exchange
~~~~~~~~~~~~~~~~~~~~~~~~

The temporary authorization code provided from the initial authorization response must be exchanged for a User Session Token before user authentication through the Client Application can take place.

The Client Application must make the following request in order to facilitate this exchange:

.. code:: yaml

    URL: https://augur.example.com/api/unstable/user/session/generate
    arguments:
        code: [the temporary authorization code]
        grant_type: "code"
    headers:
        Authorization: Client [your client secret]

The authorization server will respond with the following on success:

.. code:: json

    {
        "status": "Validated",
        "username": "the username associated with this request",
        "access_token": "the new Bearer token",
        "refresh_token": "the new refresh token",
        "token_type": "Bearer",
        "expires": [integer: seconds until this access_token expires]
    }

Success!
~~~~~~~~~

Now that the temporary code exchange is complete, your application has the authorization required to make requests on behalf of the logged-in user.

Refreshing Sessions
~~~~~~~~~~~~~~~~~~~~

When a User Session Token expires, the Client Application has two options for reauthorization. The application may ask the user to manually reauthenticate by presenting a link or button which restarts the authentication flow.

The application may also attempt automatic reauthorization using the previously provided refresh token. Refreshing a User Session Token can be done with the following request:

.. code:: yaml

    URL: https://augur.example.com/api/unstable/user/session/refresh
    arguments:
        refresh_token: [the previously provided refresh token]
        grant_type: "refresh_token"
    headers:
        Authorization: Client [your client secret]

The authorization server will respond with the following on success:

.. code:: json

    {
        "status": "Validated",
        "access_token": "the new Bearer token",
        "refresh_token": "the new refresh token",
        "token_type": "Bearer",
        "expires": [integer: seconds until this access_token expires]
    }

The new User Session and refresh tokens should replace the existing tokens, as they may not be the same.

See the rest API documentation for more specific details about these login endpoints.

Making Authenticated Requests
------------------------------

Once the User Session Token has been acquired, authenticated requests must be made using both the Client Secret and the Bearer Token. Authentication credentials must be provided in the ``Authorization`` header as such::

    Authorization: Client [Client Secret], Bearer [User Session Token]

**Please note that both the Client Secret and the User Sesson Token must be included in the Authorization header for authenticated requests**
