#Import agent from assistant.py and execute the agent
from agent.assistant import create_agent

# Create the agent and execute it to handle user interactions and perform tasks
agent = create_agent()

user_input = input("How can I assist you with your emails today? ")
agent.invoke({"messages": [{"role": "user", "content": user_input}]})

response = agent.invoke({"messages": [{"role": "user", "content": user_input}]})
print(response['messages'][-1].content)
