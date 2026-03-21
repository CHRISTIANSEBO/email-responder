from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

# Paths resolved relative to this file, not the working directory
_BASE_DIR = Path(__file__).parent.parent
_TOKEN_PATH = _BASE_DIR / 'token.json'
_CREDENTIALS_PATH = _BASE_DIR / 'credentials.json'

def _load_credentials() -> Credentials:
    """Load, refresh, and return OAuth credentials. Does not build a service."""
    if not _CREDENTIALS_PATH.exists():
        raise FileNotFoundError(
            f"credentials.json not found at {_CREDENTIALS_PATH}. "
            "Download it from Google Cloud Console and place it in the project root."
        )

    creds = None

    if _TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(_TOKEN_PATH), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            try:
                creds.refresh(Request())
            except Exception:
                # Token revoked or expired — delete it and re-authenticate
                _TOKEN_PATH.unlink(missing_ok=True)
                creds = None
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(str(_CREDENTIALS_PATH), SCOPES)
            creds = flow.run_local_server(port=0, prompt='consent')

        with open(_TOKEN_PATH, 'w') as token:
            token.write(creds.to_json())

    return creds


def authenticate_gmail():
    """Load credentials and build a Gmail API service instance."""
    creds = _load_credentials()
    return build('gmail', 'v1', credentials=creds)
