import asyncio
import datetime
import inspect
import os
from typing import Optional

from . import assistants, llms, runs, threads
from ._logging import logger as log
from ._tools import get_tool
from .llms import Usage
from .messages import MessageCreate
from .messages import create as create_message
from .messages import list as list_messages
from .tools import Context, Tool


async def chat_complete(run: runs.RunRead, iter):
    try:
        thread_id = run.thread_id

        messages = []

        model = run.model
        instructions = run.instructions
        tools = run.tools
        run_metadata = run.metadata if run.metadata else {}
        file_ids = []

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

            if assistant.file_ids:
                file_ids.extend(assistant.file_ids)

        # Get Thread
        thread = threads.get(id=thread_id)

        # set instructions
        if instructions is not None and len(instructions) > 0:
            messages.append({
                "role": "system",
                "content": instructions
            })

        # llm_args
        llm_args = run_metadata['llm_args'] if 'llm_args' in run_metadata else {"temperature": 0.0}

        # Laod history
        history_limit = run_metadata['history_limit'] if 'history_limit' in run_metadata else 7
        if not isinstance(history_limit, int):
            history_limit = 0
        history = list_messages(thread_id=thread_id, order="desc", limit=history_limit).data
        history = history[::-1]

        # append history to messages
        for h in history:
            role = h.role
            content = h.content[0]
            if content.type == "text":
                content = content.text[0].value
            messages.append({
                "id": h.id,
                "role": role,
                "content": content,
                "metadata": h.metadata,
                "created_at": h.created_at
            })

        # Message file_ids
        if len(history) > 0:
            last = history[-1]
            if last.role == "user" and last.file_ids:
                file_ids.extend(last.file_ids)

        file_ids = list(set(file_ids))

        runs.update(
            id=run.id,
            status="in_progress",
            started_at=int(round(datetime.datetime.now().timestamp()))
        )

        stream = False
        if run_metadata.get("stream"):
            stream = True

        # Run tools
        context: Context = await run_tools(
                assistant=assistant,
                run=run,
                thread=thread,
                tools=tools,
                messages=messages,
                run_metadata=run_metadata,
                file_ids=file_ids
            )
        llm_args.update(context.llm_args)

        # llm timeout
        if 'timeout' not in llm_args and 'LLM_HTTP_TIMEOUT' in os.environ:
            try:
                timeout = int(os.environ.get('LLM_HTTP_TIMEOUT'))
                llm_args['timeout'] = timeout
            except:
                pass

        log.debug(f"Context after tools: {context}")

        genereated = []
        usage = Usage()

        if context.is_completed:
            completed_msg = context.messages[-1]["content"]
            genereated.append(completed_msg)
            await iter.put(completed_msg)
        else:
            combined_messages = combine_system_messages(messages=context.messages)
            llm = llms.get(model_name=model)

            resp = await llm.chat(messages=combined_messages, stream=stream, usage=usage, **llm_args)

            if stream:
                async for c in resp:
                    if c is not None:
                        genereated.append(c)
                        await iter.put(c)
                        await asyncio.sleep(0) # back to envent loop for iter.get
            else:
                genereated.append(resp)

        msg_metadata = context.message_metadata
        msg_metadata["usage"] = {"prompt_tokens": usage.prompt_tokens, "completion_tokens": usage.completion_tokens}

        msg_create = MessageCreate(
            role="assistant",
            content=''.join(genereated),
            metadata=msg_metadata
        )
        create_message(thread_id=thread_id, message=msg_create, assistant_id=assistant_id, run_id=run.id, user_id=run.user_id, org_id=run.org_id)

        runs.update(
            id=run.id,
            status="completed",
            completed_at=int(round(datetime.datetime.now().timestamp()))
        )
        await iter.put(None) # Completed
    except Exception as e:
        log.warn(f"LLM Failed: ", exc_info=e)

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


async def run_tools(assistant, run, thread, tools, messages, run_metadata, file_ids=[]):
    run_metadata = run_metadata if run_metadata else {}

    context = Context(
            messages=messages,
            run_metadata=run_metadata,
            file_ids=file_ids,
            assistant=assistant,
            run=run,
            thread=thread
        )

    if not tools:
        tools = []

    for tool in tools:
        tool_name = tool["type"]

        #if tool_name.startswith("$"):
        #    # 由 LLM 决定是否执行, 并确定执行参数

        tool_instance: Optional[Tool] = get_tool(tool_name)

        if tool_instance is None or not isinstance(tool_instance, Tool):
            log.warn(f"tool instance is not a Tool: name={tool_name}, instance={tool_instance}")
            continue

        if inspect.iscoroutinefunction(tool_instance.execute):
            await tool_instance.execute(context=context)
        else:
            await asyncio.get_running_loop().run_in_executor(
                None,
                tool_instance.execute,
                context
            )

        if context.is_completed:
            return context

    return context


def combine_system_messages(messages):
    """Combine multiple system messages into one"""
    normal_messages = []
    system_message = []
    for msg in messages:
        if msg["role"] == "system":
            system_message.append(msg["content"])
        else:
            normal_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
    r_messages = []
    if len(system_message) > 0:
        r_messages.append(
            {
                "role": "system",
                "content": '\n'.join(system_message)
            }
        )
    r_messages.extend(normal_messages)
    return r_messages
