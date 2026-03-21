# Jean — AI Email Assistant

A personal AI email assistant that reads, sorts, and responds to your Gmail through a conversational chat interface.

## The Problem
Managing a busy inbox is time-consuming. Spam and low-priority emails bury the important ones, and switching between compose, search, and settings to unsubscribe breaks your flow.

## Solution
Jean is a ReAct agent powered by Claude that handles your inbox through natural conversation. Read emails, sort by urgency, compose and send replies, and unsubscribe from senders — all without leaving a single interface. Actions that send or open private content require your explicit confirmation before Jean proceeds.

![Jean chat interface](https://i.imgur.com/placeholder.png)

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18, TypeScript, Vite |
| Animations | GSAP (staggered menu, split-text entry) |
| Backend | Flask, Python 3 |
| Agent | LangGraph ReAct + LangChain |
| LLM | Anthropic Claude (claude-haiku-4-5) |
| Email | Gmail API, Google OAuth 2.0 |
| Persistence | SQLite (chat history) |

## Features

- **Conversational inbox control** — natural language commands to read, sort, send, and unsubscribe
- **Confirmation flow** — Jean asks before opening emails or sending anything on your behalf
- **Category filtering** — read Primary, Promotions, Social, Updates, or Forums separately
- **Urgency sorting** — ranks emails by keyword signals (urgent, deadline, action required, etc.)
- **Parallel fetching** — email headers fetched concurrently via `ThreadPoolExecutor`
- **Chat history** — conversations saved to SQLite and restored across sessions
- **Animated UI** — GSAP-powered staggered menu and character-level text animations

## Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- An [Anthropic API key](https://console.anthropic.com/)
- A Google Cloud project with Gmail API enabled

### 1. Clone and install Python dependencies
```bash
git clone https://github.com/CHRISTIANSEBO/email-responder.git
cd email-responder
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### 2. Install frontend dependencies
```bash
cd client
npm install
cd ..
```

### 3. Add your Anthropic API key
Create a `.env` file in the project root:
```
ANTHROPIC_API_KEY=your_key_here
```

### 4. Add Gmail credentials
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the **Gmail API**
3. Create an **OAuth 2.0 Client ID** (Desktop app)
4. Download `credentials.json` and place it in the project root
5. Add these scopes to your OAuth consent screen:
   - `https://www.googleapis.com/auth/gmail.readonly`
   - `https://www.googleapis.com/auth/gmail.send`

### 5. Run the app

In one terminal — start the Flask backend:
```bash
python server.py
```

In another terminal — start the frontend:
```bash
cd client
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

On first run, a browser window will open for Gmail OAuth. A `token.json` is saved automatically for future runs.

## Project Structure
```
email-responder/
├── .env                    # Anthropic API key (not committed)
├── .gitignore
├── server.py               # Flask API server
├── main.py                 # Terminal REPL (alternative entry point)
├── requirements.txt
├── chats.db                # SQLite chat history (auto-created)
├── credentials.json        # Google OAuth credentials (not committed)
├── token.json              # Gmail OAuth token (auto-created, not committed)
├── agent/
│   ├── assistant.py        # LangGraph agent + system prompt
│   ├── file_handler.py     # Gmail OAuth flow with auto-refresh
│   └── tools.py            # Gmail tools (read, send, sort, open, unsubscribe)
├── client/
│   ├── src/
│   │   ├── App.tsx          # Main chat UI
│   │   ├── StaggeredMenu.tsx # GSAP-animated overlay navigation
│   │   ├── DarkVeil.tsx     # Animated background
│   │   └── SplitText.tsx    # Character-level text animation
│   └── vite.config.ts
└── tests/
    └── test_tools.py
```

## Tools

| Tool | Description |
|------|-------------|
| `read_email` | Fetch the latest 10 emails; optionally filter by category |
| `sort_emails` | Rank emails by urgency keywords |
| `open_email` | Open a specific email in full — requires your confirmation |
| `send_email` | Compose and send an email — shows a preview, requires your confirmation |
| `summarize_email` | Summarize the subject, sender, and body of an email |
| `unsubscribe_from_email` | Unsubscribe from a sender via their List-Unsubscribe header — requires your confirmation |

## Running Tests
```bash
python -m pytest tests/ -v
```

## Note on Deployment
Jean is designed as a personal tool. The Gmail OAuth flow requires each user to authenticate with their own Google account via Google Cloud Console. For a publicly hosted version, a multi-user OAuth web flow and per-session state management would be required.
