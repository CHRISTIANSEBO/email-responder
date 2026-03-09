# This file defines tools for the email responder agent.
from langchain.tools import tool
from email.mime.text import MIMEText
import base64 
from agent.file_handler import authenticate_gmail

# Authenticate with Gmail once and reuse the service object for all tools
service = authenticate_gmail()


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
        emails.append({
            'subject': next(header['value'] for header in msg_data['payload']['headers'] if header['name'] == 'Subject'),
            'sender': next(header['value'] for header in msg_data['payload']['headers'] if header['name'] == 'From'),
            'snippet': msg_data['snippet']
        })

    return emails

# Define a tool to send an email using Gmail
@tool
def send_email(to, subject, body):
    """send an email using gmail."""
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
    return f"Subject: {msg['subject']}\nFrom: {msg['sender']}\nSummary: {msg['snippet']}"

# Define a tool to sort emails by priority 
@tool
def sort_emails(msg):
    """Sort emails by priority."""
    # Sort emails based on sender and body content
    subject = msg['payload']['headers'][0]['value']
    body = base64.urlsafe_b64decode(msg['payload']['parts'][0]['body']['data']).decode('utf-8')
    
    return f"Subject: {subject}\nBody: {body}"

# Define a tool to unsubscribe from an email sender
@tool
def unsubscribe_from_email(sender_email: str):
    """Unsubscribe from a sender by finding the List-Unsubscribe header in their latest email and sending an unsubscribe request."""
    # Search for the latest email from the sender
    results = service.users().messages().list(userId='me', q=f'from:{sender_email}', maxResults=1).execute()
    messages = results.get('messages', [])

    if not messages:
        return f"No emails found from {sender_email}."

    msg_data = service.users().messages().get(userId='me', id=messages[0]['id'], format='full').execute()
    headers = msg_data['payload']['headers']

    # Look for the List-Unsubscribe header
    unsubscribe_header = next(
        (h['value'] for h in headers if h['name'].lower() == 'list-unsubscribe'),
        None
    )

    if not unsubscribe_header:
        return f"No unsubscribe option found in emails from {sender_email}."

    # Prefer mailto: unsubscribe over URL
    import re
    mailto_match = re.search(r'<mailto:([^>]+)>', unsubscribe_header)
    if mailto_match:
        unsubscribe_address = mailto_match.group(1)
        # Parse optional subject from mailto (e.g. mailto:unsub@example.com?subject=unsubscribe)
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

    # Fall back to returning the URL for the user to visit
    url_match = re.search(r'<(https?://[^>]+)>', unsubscribe_header)
    if url_match:
        return f"To unsubscribe, visit: {url_match.group(1)}"

    return f"Could not parse unsubscribe info from header: {unsubscribe_header}"