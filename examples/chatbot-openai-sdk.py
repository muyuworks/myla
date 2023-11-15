import time
import openai

openai.base_url = "http://localhost:2000/api/v1/"
openai.api_key = "sk-xxx"

assistant = openai.beta.assistants.create(
    name="Chatbot",
    instructions="Your are a usefull assistant.",
    tools=[],
    model="Qwen-14B-Chat-Int4"
)
print(f"Assistant created, id:{assistant.id}")

thread = openai.beta.threads.create()
print(f"Thread created, id:{thread.id}")

message = openai.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content="你们有什么产品？"
)
print(f"User message created, id: {message.id}, content={message.content[0].text[0]['value']}")

def list_messages(thread):
    messages = openai.beta.threads.messages.list(
        limit=20,
        thread_id=thread.id
    )
    print("Messages: ")
    for msg in messages:
        print(f"\tid: {msg.id}, role: {msg.role}, content: {msg.content[0].text[0]['value']}")

list_messages(thread=thread)

run = openai.beta.threads.runs.create(
  thread_id=thread.id,
  assistant_id=assistant.id,
  instructions="你是牧语工场的客服，负责回答牧语工场客户的问题",
  tools=[{"type": "$iur"}, {"type": "retrieval"}],
  metadata={"retrieval_vs_name": "default"}
)
print(f"Run created, id: {run.id}")

def check_run_status(thread, run):
    run = openai.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )
    print(f"Check run status, run_id:{run.id}, status: {run.status}")
    return run

for i in range(10):
    time.sleep(3)
    r = check_run_status(thread=thread, run= run)
    if r.status == "completed":
        list_messages(thread=thread)
        break

print("Done.")