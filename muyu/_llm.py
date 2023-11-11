import os
import json
import datetime
import openai
from .tools import get_tool
from . import hook
from . import messages, runs, assistants
from ._logging import logger as log
from .retrieval import Retrieval

async def chat_complete(run: runs.RunRead, iter):
    try:
        thread_id = run.thread_id

        llm_messages = []

        model = run.model
        instructions = run.instructions
        tools = run.tools
        run_metadata = run.metadata if run.metadata else {}

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

            a_metadata = assistant.metadata if assistant.metadata else {}
            a_metadata.update(run_metadata)
            run_metadata = a_metadata

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
        
        llm_messages, args, metadata = await run_tools(tools=tools, msgs=llm_messages, metadata=run_metadata)
        log.debug(f"Messages sumit to LLM: {llm_messages}")

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
            metadata=metadata
        )
        messages.create(thread_id=thread_id, message=msg_generated, assistant_id=assistant_id, run_id=run.id)

        runs.update(
            id=run.id,
            status="completed",
            completed_at=int(round(datetime.datetime.now().timestamp()))
        )
        await iter.put(None) # Completed
    except Exception as e:
        log.info(f"LLM Failed: {e}")
        log.debug("LLM exc: ", exc_info=e)
        
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

async def run_tools(tools, msgs, metadata):
    args = {}
    metadata = metadata if metadata else {}
    for tool in tools:
        tool_name = tool["type"]
        tool_instance = get_tool(tool_name)
        
        if tool_instance and isinstance(tool_instance, hook.Hook):
            msgs, args, metadata = await run_hook(msgs=msgs, metadata=metadata, tool=tool_instance)
        elif tool_instance and isinstance(tool_instance, Retrieval):
            msgs, metadata = await retrieval(msgs=msgs, metadata=metadata, tool=tool_instance)
    return msgs, args, metadata

async def run_hook(msgs, metadata, tool):
    args = {}
    metadata = metadata if metadata else {}

    msgs, n_args, n_metadata = await tool.before(messages=msgs)
    if n_args:
        args.update(n_args)
    if n_metadata:
        metadata.update(n_metadata)
    return msgs, args, metadata

async def retrieval(msgs, metadata, tool):
    
    if len(msgs) < 0:
        log.debug("Message is empty, skip retrieval")
        return msgs, metadata
    
    if not metadata or "retrieval_collection_name" not in metadata:
        log.debug("retrieval_collection_name is empty, skip retrieval")
        return msgs, metadata
    
    vs_name = metadata["retrieval_collection_name"]
    args = {}
    if "retrieval_top_k" in metadata:
        args["top_k"] = metadata["retrieval_top_k"]

    query = msgs[-1]["content"]
    
    docs = await tool.search(vs_name=vs_name, query=query, **args)
    msgs.append({
        "role": "system",
        "content": json.dumps(docs, ensure_ascii=False)
    })

    return msgs, metadata