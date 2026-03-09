import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

# Authenticate and create the Gmail API service
def authenticate_gmail():
    creds = None

    # Check if token.json exists and load credentials
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no valid credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
        # Refresh the token if it has expired
            from google.auth.transport.requests import Request
            creds.refresh(Request())
        else:
            # Run the full login flow if no valid credentials exist
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0, prompt='consent')

    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    
    # Build and return the Gmail API service
    service = build('gmail', 'v1', credentials=creds)
    return service
