from myla import llms
import dotenv

dotenv.load_dotenv(".env")

llm = llms.get("gpt-3.5-turbo")

resp = llm.sync_generate(instructions="hi")
print(resp)

resp = llm.sync_chat(messages=[{"role": "user", "content": "hi"}], stream=True)
for r in resp:
    print(r, end='', flush=True)
print("\n")
