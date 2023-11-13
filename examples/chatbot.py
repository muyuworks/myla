"""
import time
import asyncio
from dotenv import load_dotenv
import myla

# Load settings
load_dotenv(".env")

async def main():
    # Create an assistant
    assistant_create = myla.assistants.AssistantCreate(
        name="Chatbot",
        instructions="Your are a usefull assistant.",
        tools=[],
        model="Qwen-14B-Chat-Int4"
    )
    assistant = myla.assistants.create(assistant_create)
    print(f"Assistant created: {assistant.name} {assistant.id}")

    # Create a thread
    thread_create = myla.threads.ThreadCreate()
    thread = myla.threads.create(thread_create)
    print(F"Thread created: {thread.id}")

    # Create a message
    message_create = myla.messages.MessageCreate(
        thread_id=thread.id,
        role="user",
        content="hi"
    )
    message = myla.messages.create(
        thread_id=thread.id, 
        assistant_id=assistant.id, 
        message=message_create)
    print(f"Message created: {message.id}")

    run_create = myla.runs.RunCreate(
        thread_id=thread.id,
        assistant_id=assistant.id,
        tools=[{"type": "$iur"}]
    )
    run = myla.runs.create(thread_id=thread.id, run=run_create)
    print(f"Run created: {run.id}")

    while True:

        r = myla.runs.get(thread_id=thread.id, run_id=run.id)
        print(f"Run status: {r.status}, id={run.id}")
        if r.status == "completed" or r.status == "failed":
            msgs = myla.messages.list(thread_id=thread.id)
            print(f"Thread messages: {msgs}")
        else:
            time.sleep(2)

loop = asyncio.get_event_loop()

loop.run_until_complete(main())
"""