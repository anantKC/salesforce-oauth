import threading
import webbrowser
import uvicorn
from requests_oauthlib import OAuth2Session
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route
from decouple import config

# Salesforce OAuth2 credentials
client_id = config('client_id')
client_secret = config('client_secret')
redirect_uri = config('redirect_uri')  # This should match the callback URL configured in your Salesforce Connected App
authorization_base_url = 'https://login.salesforce.com/services/oauth2/authorize'
token_url = 'https://login.salesforce.com/services/oauth2/token'

# Event to signal the main thread when the authorization code is received
authorization_code_event = threading.Event()

# Set up a simple Starlette app to handle the OAuth2 redirect URI and capture the code
async def callback(request):
    global authorization_code
    authorization_code = request.query_params.get('code')
    print(f'Authorization code: {authorization_code}')
    authorization_code_event.set()  # Signal the main thread
    return PlainTextResponse('Authorization Successful. You can close this page.')

app = Starlette(routes=[Route('/services/oauth2/success/', callback)])

# Run the Starlette app using Uvicorn server
server_thread = threading.Thread(target=uvicorn.run, kwargs={'app': app, 'host': 'localhost', 'port': 8000})
server_thread.daemon = True
server_thread.start()

# Obtain authorization URL
salesforce = OAuth2Session(client_id, redirect_uri=redirect_uri)
authorization_url, _ = salesforce.authorization_url(authorization_base_url)

# Open the authorization URL in the default web browser
webbrowser.open(authorization_url)

# Wait for the authorization code to be captured
authorization_code_event.wait()

# Exchange authorization code for an access token
token = salesforce.fetch_token(
    token_url,
    code=authorization_code,
    client_secret=client_secret
)
access_token = token['access_token']
print(f'Access Token: {access_token}')
