from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

# Paths resolved relative to this file, not the working directory
_BASE_DIR = Path(__file__).parent.parent
_TOKEN_PATH = _BASE_DIR / 'token.json'
_CREDENTIALS_PATH = _BASE_DIR / 'credentials.json'

# Authenticate and create the Gmail API service
def authenticate_gmail():
    if not _CREDENTIALS_PATH.exists():
        raise FileNotFoundError(
            f"credentials.json not found at {_CREDENTIALS_PATH}. "
            "Download it from Google Cloud Console and place it in the project root."
        )

    creds = None

    # Check if token.json exists and load credentials
    if _TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(_TOKEN_PATH), SCOPES)

    # If there are no valid credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Refresh the token if it has expired
            from google.auth.transport.requests import Request
            creds.refresh(Request())
        else:
            # Run the full login flow if no valid credentials exist
            flow = InstalledAppFlow.from_client_secrets_file(str(_CREDENTIALS_PATH), SCOPES)
            creds = flow.run_local_server(port=0, prompt='consent')

    # Save the credentials for the next run
    with open(_TOKEN_PATH, 'w') as token:
        token.write(creds.to_json())

    # Build and return the Gmail API service
    service = build('gmail', 'v1', credentials=creds)
    return service
