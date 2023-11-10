import os
import datetime
import openai
from . import messages, runs, assistants

async def chat_complete(run: runs.RunRead, iter):
    try:
        thread_id = run.thread_id

        history = []

        model = run.model
        instructions = run.instructions

        # Get Assistant
        assistant = assistants.get(id=run.assistant_id)
        assistant_id = None
        if assistant is not None:
            assistant_id = assistant.id

            if not instructions:
                instructions = assistant.instructions
            if not model:
                model = assistant.model

        if instructions is not None:
            history.append({
                "role": "system",
                "content": instructions
            })

        # Laod history
        msgs = messages.list(thread_id=thread_id)

        for msg in msgs.data:
            role = msg.role
            content = msg.content[0]
            if content.type == "text":
                content = content.text[0].value
            history.append({
                "role": role,
                "content": content
            })

        runs.update(
            id=run.id,
            status="in_progress",
            started_at=int(round(datetime.datetime.now().timestamp()))
        )

        # print(f"Task run, run_id: {run.id}, message: {history}")
        api_key = os.environ.get("LLM_API_KEY")
        endpoint = os.environ.get("LLM_ENDPOINT")

        llm = openai.OpenAI(api_key=api_key, base_url=endpoint)

        resp = llm.chat.completions.create(
            model=model,
            messages=history,
            stream=True,
        )

        genereated = []
        for r in resp:
            c = r.choices[0].delta.content
            if c is not None:
                genereated.append(c)
                await iter.put(c)

        msg_generated = messages.MessageCreate(
            role="assistant",
            content=''.join(genereated)
        )
        messages.create(thread_id=thread_id, message=msg_generated, assistant_id=assistant_id, run_id=run.id)

        runs.update(
            id=run.id,
            status="completed",
            completed_at=int(round(datetime.datetime.now().timestamp()))
        )
        await iter.put(None) # Completed
    except Exception as e:
        print(e)
        runs.update(id=run.id,
            status="failed",
            last_error={
                "code": "server_error",
                "message": str(e)
            },
            failed_at=int(round(datetime.datetime.now().timestamp()))
        )
        await iter.put(e)
        await iter.put(None) #DONE