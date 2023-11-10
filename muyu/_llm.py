import os
import traceback
import datetime
import openai
from .tools import get_tool
from . import hook
from . import messages, runs, assistants

async def chat_complete(run: runs.RunRead, iter):
    try:
        thread_id = run.thread_id

        llm_messages = []

        model = run.model
        instructions = run.instructions
        tools = run.tools

        # Get Assistant
        assistant = assistants.get(id=run.assistant_id)
        assistant_id = None
        if assistant is not None:
            assistant_id = assistant.id

            if not instructions:
                instructions = assistant.instructions
            if not model:
                model = assistant.model
            if not tools or len(tools) == 0:
                tools = assistant.tools

        if instructions is not None:
            llm_messages.append({
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
            llm_messages.append({
                "role": role,
                "content": content
            })

        runs.update(
            id=run.id,
            status="in_progress",
            started_at=int(round(datetime.datetime.now().timestamp()))
        )

        # Before hooks
        llm_messages, args, metadate = await before_hooks(messages=llm_messages, tools=tools)

        # print(f"Task run, run_id: {run.id}, message: {history}")
        api_key = os.environ.get("LLM_API_KEY")
        endpoint = os.environ.get("LLM_ENDPOINT")

        llm = openai.OpenAI(api_key=api_key, base_url=endpoint)

        resp = llm.chat.completions.create(
            model=model,
            messages=llm_messages,
            stream=True,
            **args
        )

        genereated = []
        for r in resp:
            c = r.choices[0].delta.content
            if c is not None:
                genereated.append(c)
                await iter.put(c)

        msg_generated = messages.MessageCreate(
            role="assistant",
            content=''.join(genereated),
            metadata=metadate
        )
        messages.create(thread_id=thread_id, message=msg_generated, assistant_id=assistant_id, run_id=run.id)

        runs.update(
            id=run.id,
            status="completed",
            completed_at=int(round(datetime.datetime.now().timestamp()))
        )
        await iter.put(None) # Completed
    except Exception as e:
        traceback.print_exc()
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

async def before_hooks(messages, tools):
    args = {}
    metadata = {}
    for tool in tools:
        tool_name = tool["type"]
        tool_instance = get_tool(tool_name)
        
        if tool_instance and isinstance(tool_instance, hook.Hook):
            messages, n_args, n_metadata = await tool_instance.before(messages=messages)
            if n_args:
                args.update(n_args)
            if n_metadata:
                metadata.update(n_metadata)
    return messages, args, metadata