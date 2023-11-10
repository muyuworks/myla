import time
import openai

openai.base_url = "http://localhost:2000/v1/"
openai.api_key = "sk-xxx"

assistant = openai.beta.assistants.create(
    name="Chatbot",
    instructions="Your are a usefull assistant.",
    tools=[],
    model="gpt-3.5-turbo"
)
print(f"Assistant created, id:{assistant.id}")

thread = openai.beta.threads.create()
print(f"Thread created, id:{thread.id}")

message = openai.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="hi"
)
print(f"User message created, id: {message.id}, content={message.content[0].text[0]['value']}")

def list_messages(thread):
    messages = openai.beta.threads.messages.list(
        thread_id=thread.id
    )
    print("Messages: ")
    for msg in messages:
        print(f"\tid: {msg.id}, role: {msg.role}, content: {msg.content[0].text[0]['value']}")

list_messages(thread=thread)

run = openai.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=assistant.id,
  instructions="Please address the user as Jane Doe. The user has a premium account."
)
print(f"Run created, id: {run.id}")

def check_run_status(thread, run):
    run = openai.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )
    print(f"Check run status, run_id:{run.id}, status: {run.status}")
    return run

for i in range(3):
    time.sleep(3)
    r = check_run_status(thread=thread, run= run)
    if r.status == "completed":
        list_messages(thread=thread)
        break

print("Done.")