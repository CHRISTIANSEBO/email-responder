# import gmail authentication function from file_handler.py
from agent.file_handler import authenticate_gmail

# Authenticate with Gmail 
service = authenticate_gmail()
print("Gmail authenticated successfully.")
