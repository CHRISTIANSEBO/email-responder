# This file defines a function to create a LangGraph ReAct agent using the Anthropic API and custom tools for email handling.
import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from agent.tools import read_email, send_email, summarize_email, sort_emails, unsubscribe_from_email

load_dotenv()
# Function to create and return a LangGraph ReAct agent
def create_agent(checkpointer=None):
    """Create and return a LangGraph ReAct agent."""
    llm = ChatAnthropic(
        model="claude-sonnet-4-6",
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )

    tools = [read_email, send_email, summarize_email, sort_emails, unsubscribe_from_email]

    # Create a ReAct agent using LangGraph
    agent = create_react_agent(llm, tools, checkpointer=checkpointer)

    return agent