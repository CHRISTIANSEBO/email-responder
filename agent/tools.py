# This file defines tools for the email responder agent.
from langchain.tools import tool
from email.mime.text import MIMEText
import base64
import re
from agent.file_handler import authenticate_gmail


def _extract_body(payload: dict) -> str:
    """Recursively extract plain-text body from a Gmail message payload."""
    mime_type = payload.get('mimeType', '')
    if mime_type == 'text/plain':
        data = payload.get('body', {}).get('data', '')
        return base64.urlsafe_b64decode(data + '==').decode('utf-8', errors='replace') if data else ''
    if 'parts' in payload:
        # Prefer text/plain; fall back to text/html
        plain = next((p for p in payload['parts'] if p.get('mimeType') == 'text/plain'), None)
        part = plain or next((p for p in payload['parts'] if p.get('mimeType') == 'text/html'), None)
        if part:
            return _extract_body(part)
    return ''

# Authenticate with Gmail once and reuse the service object for all tools
try:
    service = authenticate_gmail()
except FileNotFoundError as e:
    raise SystemExit(f"Authentication error: {e}")
except Exception as e:
    raise SystemExit(f"Failed to authenticate with Gmail: {e}")


# Define a tool to read the latest 10 emails from Gmail
@tool
def read_email():
    """read the latest 10 emails from gmail."""
    results = service.users().messages().list(userId='me', maxResults=10).execute()
    messages = results.get('messages', [])

    # Fetch the full email data for each message
    emails = []
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        headers = msg_data['payload']['headers']
        emails.append({
            'subject': next((h['value'] for h in headers if h['name'] == 'Subject'), '(no subject)'),
            'sender': next((h['value'] for h in headers if h['name'] == 'From'), '(unknown)'),
            'body': _extract_body(msg_data['payload']),
        })

    return emails

# Define a tool to send an email using Gmail
_EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

@tool
def send_email(to, subject, body):
    """send an email using gmail."""
    if not _EMAIL_RE.match(to):
        return f"Invalid recipient email address: {to}"
    # Create the email message
    message = MIMEText(body)
    message['to'] = to
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    # Send the email
    service.users().messages().send(userId='me', body={'raw': raw_message}).execute()

    return "Email sent successfully."

# Define a tool to summarize the content of an email
@tool
def summarize_email(msg: dict):
    """Summarize the content of an email."""
    return f"Subject: {msg['subject']}\nFrom: {msg['sender']}\nBody: {msg['body']}"

# Define a tool to sort emails by priority
URGENT_KEYWORDS = ['urgent', 'asap', 'important', 'action required', 'deadline', 'critical', 'immediately']

@tool
def sort_emails():
    """Fetch the latest 10 emails and sort them by urgency based on subject keywords."""
    results = service.users().messages().list(userId='me', maxResults=10).execute()
    messages = results.get('messages', [])

    emails = []
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        headers = msg_data['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '(no subject)')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), '(unknown)')
        body = _extract_body(msg_data['payload'])
        text = (subject + ' ' + body).lower()
        priority = sum(1 for kw in URGENT_KEYWORDS if kw in text)
        emails.append({'subject': subject, 'sender': sender, 'body': body, 'priority': priority})

    emails.sort(key=lambda e: e['priority'], reverse=True)
    return emails

# Define a tool to unsubscribe from an email sender
@tool
def unsubscribe_from_email(sender_email: str):
    """Unsubscribe from a sender by finding the List-Unsubscribe header in their latest email and sending an unsubscribe request."""
    if not _EMAIL_RE.match(sender_email):
        return f"Invalid sender email address: {sender_email}"
    try:
        results = service.users().messages().list(userId='me', q=f'from:{sender_email}', maxResults=1).execute()
        messages = results.get('messages', [])

        if not messages:
            return f"No emails found from {sender_email}."

        msg_data = service.users().messages().get(userId='me', id=messages[0]['id'], format='full').execute()
        headers = msg_data['payload']['headers']

        unsubscribe_header = next(
            (h['value'] for h in headers if h['name'].lower() == 'list-unsubscribe'),
            None
        )

        if not unsubscribe_header:
            return f"No unsubscribe option found in emails from {sender_email}."

        # Prefer mailto: unsubscribe over URL
        mailto_match = re.search(r'<mailto:([^>]+)>', unsubscribe_header)
        if mailto_match:
            unsubscribe_address = mailto_match.group(1)
            if '?subject=' in unsubscribe_address:
                address, subject_part = unsubscribe_address.split('?subject=', 1)
                subject = subject_part
            else:
                address = unsubscribe_address
                subject = 'Unsubscribe'

            message = MIMEText('')
            message['to'] = address
            message['subject'] = subject
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
            return f"Unsubscribe email sent to {address}."

        url_match = re.search(r'<(https?://[^>]+)>', unsubscribe_header)
        if url_match:
            return f"To unsubscribe from {sender_email}, visit: {url_match.group(1)}"

        return f"Could not parse unsubscribe info from header: {unsubscribe_header}"

    except Exception as e:
        return f"Failed to unsubscribe from {sender_email}: {type(e).__name__}: {e}"