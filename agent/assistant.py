# This module defines the Assistant class, which is responsible for handling user interactions and executing tasks using the ReAct agent framework.
import os

# Load environment variables from .env file
from dotenv import load_dotenv

# Import ReAct prompt template for guiding the agent's reasoning process
from langchain import hub

# Import LangChain agent creation and execution utilities
from langchain.agents import create_react_agent, AgentExecutor

# Import Anthropic language model for generating responses
from langchain_anthropic import ChatAnthropic

# Import tools for the agent
from agent.tools import read_email, send_email, summarize_email, sort_emails


load_dotenv()

# Create and return a ReAct agent with the defined tools
def create_agent():
    """Create and return a ReAct agent with the defined tools."""
    # Initialize the Anthropic language model with the API key from environment variables
    llm = ChatAnthropic(
        model="claude-sonnet-4-5", #Specify the model to use
        api_key = os.getenv("ANTHROPIC_API_KEY")
    )

    # Load the ReAct prompt template from the LangChain Hub
    prompt = hub.pull("hwchase17/react")
    # Define the tools that the agent can use to interact with Gmail and process emails
    tools = [read_email, send_email, summarize_email, sort_emails]
    agent = create_react_agent(llm, tools, prompt)

    return AgentExecutor(agent=agent, tools=tools, verbose=True)