# AI Email Responder

An AI agent that reads, sorts, and responds to emails using the Gmail API and Claude.

## The Problem
Managing a busy inbox is time-consuming and kills productivity, especially when spam and low-priority emails bury the important ones.

## Solution
This agent automatically reads incoming emails, sorts them by priority, summarizes their contents, and drafts intelligent responses using Claude — all through the Gmail API.

## Tech Stack
- **LLM:** Anthropic Claude (claude-sonnet-4-6)
- **Agent Framework:** LangChain
- **Email API:** Gmail API (Google OAuth 2.0)
- **Language:** Python

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

4. Add your API keys — create a `.env` file in the root folder
```
   ANTHROPIC_API_KEY=your_key_here
```

5. Run the agent
```bash
   python main.py
```

## Project Structure
```
email-responder/
├── .env
├── .gitignore
├── main.py
├── requirements.txt
└── agent/
    ├── __init__.py
    ├── assistant.py
    ├── file_handler.py
    └── tools.py
```

## Features
- 📧 Read and fetch emails via Gmail API
- 🗂️ Sort emails by priority vs spam
- 📝 Summarize email contents
- 🤖 Auto-draft intelligent responses using Claude

## Status
🚧 In Progress

## Future Improvements
- Multi-agent collaboration
