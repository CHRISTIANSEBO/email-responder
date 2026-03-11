# This file defines a function to create a LangGraph ReAct agent using the Anthropic API and custom tools for email handling.
import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from agent.tools import read_email, send_email, sort_emails, unsubscribe_from_email, open_email

load_dotenv()

SYSTEM_PROMPT = """You are Jean, a sharp and dependable personal email assistant.
You help the user manage their inbox — reading, sorting, drafting, sending, and unsubscribing from emails.

Your personality:
- Friendly and concise — no unnecessary filler
- Proactive: if you notice something worth flagging (e.g. an urgent email), mention it
- Respectful of privacy: always ask before opening or sending anything

When you're unsure of a sender's email address, ask the user to confirm it before acting.
Always refer to yourself as Jean."""

# Function to create and return a LangGraph ReAct agent
def create_agent(checkpointer=None):
    """Create and return a LangGraph ReAct agent."""
    llm = ChatAnthropic(
        model="claude-sonnet-4-6",
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )

    tools = [read_email, send_email, sort_emails, unsubscribe_from_email, open_email]

    # Create a ReAct agent using LangGraph
    agent = create_react_agent(llm, tools, prompt=SYSTEM_PROMPT, checkpointer=checkpointer)

    return agent