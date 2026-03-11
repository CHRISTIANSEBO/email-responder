import os
from datetime import datetime
from langgraph.checkpoint.memory import MemorySaver
from agent.assistant import create_agent

# Initialize the agent with a memory saver for conversation history
checkpointer = MemorySaver()
agent = create_agent(checkpointer=checkpointer)
config = {"configurable": {"thread_id": "default"}}

os.makedirs("conversations", exist_ok=True)

session_start = datetime.now().strftime("%Y%m%d_%H%M%S")
conversation_file = f"conversations/{session_start}.txt"
conversation_log = []

# Main interaction loop
print("=" * 50)
print("  Hi, I'm Jean — your personal email assistant.")
print("  Type 'exit', 'quit', or 'bye' to stop.")
print("=" * 50 + "\n")
while True:
    user_input = input("You: ").strip()
    if not user_input:
        continue
    if user_input.lower() in ("exit", "quit", "bye"):
        if conversation_log:
            with open(conversation_file, "w", encoding="utf-8") as f:
                for entry in conversation_log:
                    f.write(entry)
            print(f"Conversation saved to: {conversation_file}")
        print("Jean: Talk soon!")
        break

    response = agent.invoke(
        {"messages": [{"role": "user", "content": user_input}]},
        config=config
    )
    output = response['messages'][-1].content
    print(f"\nJean: {output}\n")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conversation_log.append(f"[{timestamp}]\nYou: {user_input}\n\nAssistant: {output}\n\n")
