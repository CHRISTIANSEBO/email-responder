# AI Email Responder

An AI agent that reads, sorts, and responds to emails using the Gmail API and Claude.

## The Problem
Managing a busy inbox is time-consuming and kills productivity, especially when spam and low-priority emails bury the important ones.

## Solution
Jean, your personal email assistant, reads your emails, sorts them by urgency, and lets you send replies and unsubscribe from senders — all through a conversational interface powered by Claude. Run her in the terminal or through a browser-based chat UI.

## Tech Stack
- **LLM:** Anthropic Claude (claude-sonnet-4-6)
- **Agent Framework:** LangGraph + LangChain
- **Email API:** Gmail API (Google OAuth 2.0)
- **Web Interface:** Flask + vanilla HTML/JS
- **Language:** Python 3.x

## Setup Instructions

1. Clone the repository
```bash
git clone https://github.com/CHRISTIANSEBO/email-responder.git
cd email-responder
```

2. Create and activate a virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Add your Anthropic API key — create a `.env` file in the root folder
```
ANTHROPIC_API_KEY=your_key_here
```

5. Add your Gmail credentials — download `credentials.json` from [Google Cloud Console](https://console.cloud.google.com/) and place it in the project root. Enable the Gmail API and configure OAuth 2.0 with the following scopes:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.send`

6. Run the agent

**Terminal (REPL):**
```bash
python main.py
```

**Web UI:**
```bash
python server.py
```
Then open `http://localhost:5000` in your browser.

On first run, a browser window will open for Gmail OAuth login. A `token.json` file will be saved automatically for future runs.

## Project Structure
```
email-responder/
├── .env                  # Anthropic API key (not committed)
├── .gitignore
├── main.py               # Terminal REPL entry point
├── server.py             # Flask web server
├── requirements.txt
├── agent/
│   ├── __init__.py
│   ├── assistant.py      # Agent creation and system prompt
│   ├── file_handler.py   # Gmail OAuth authentication
│   └── tools.py          # Email tools
├── static/
│   └── index.html        # Browser chat UI
└── tests/
    └── test_tools.py     # Unit tests
```

## Tools

| Tool | Description |
|------|-------------|
| `read_email` | Fetch the latest 10 emails by inbox category (primary, promotions, social, updates, forums) |
| `sort_emails` | Fetch and rank emails by urgency keywords |
| `open_email` | Open a specific email in full — requires your confirmation first |
| `send_email` | Draft and send an email — shows a preview and requires your confirmation before sending |
| `unsubscribe_from_email` | Unsubscribe from a sender via their List-Unsubscribe header |

## Running Tests
```bash
python -m pytest tests/ -v
```

## Future Improvements
- Multi-agent collaboration
- Async email processing
- Support for email attachments
