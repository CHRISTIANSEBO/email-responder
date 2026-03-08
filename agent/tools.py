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
        emails.append(msg_data)

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
def summarize_email(msg):
    """Summarize the content of an email."""
    # Extract the relevant parts of the email for summarization
    data = msg['payload']['parts'][0]['body']['data']
    decoded = base64.urlsafe_b64decode(data).decode('utf-8')
    
    return decoded

# Define a tool to sort emails by priority 
@tool
def sort_emails(msg):
    """Sort emails by priority."""
    # Sort emails based on sender and body content
    subject = msg['payload']['headers'][0]['value']
    body = base64.urlsafe_b64decode(msg['payload']['parts'][0]['body']['data']).decode('utf-8')
    
    return f"Subject: {subject}\nBody: {body}"

    