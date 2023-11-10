import os, sys
import json
from typing import List
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import StreamingResponse
from contextlib import asynccontextmanager

from .persistence import Persistence
from sqlmodel import Session

from ._models import DeletionStatus, ListModel
from . import assistants, threads, messages, runs
from ._run_scheduler import RunScheduler
from ._run_queue import get_run_iter, create_run_iter

from . import tools, hook

API_VERSION = "v1"


@asynccontextmanager
async def lifespan(api: FastAPI):
    ext_dir = os.environ.get("EXT_DIR")
    if ext_dir:
        sys.path.append(ext_dir)
    
    tools.load_tools()

    # on startup
    Persistence.default().initialize_database()
    await RunScheduler.default().start()

    yield
    # on shutdown
    pass

tags_metadata = [
    {
        "name": "Assistants",
    },
    {
        "name": "Threads",
    },
    {
        "name": "Messages",
    },
    {
        "name": "Runs",
    },
]

# FastAPI
api = FastAPI(
    lifespan=lifespan,
    title="Muyu API",
    version=API_VERSION,
    docs_url="/swagger",
    redoc_url='/docs'
)


class Version(BaseModel):
    version: str


@api.get('/version', response_model=Version)
async def get_version():
    return Version(version=API_VERSION)

# Assistants


@api.post("/v1/assistants", response_model=assistants.AssistantRead, tags=['Assistants'])
def create_assistant(assistant: assistants.AssistantCreate):
    r = assistants.create(assistant=assistant)
    return r


@api.get("/v1/assistants/{assistant_id}", response_model=assistants.AssistantRead, tags=['Assistants'])
def retrieve_assistant(assistant_id: str):
    a = assistants.get(id=assistant_id)
    if not a:
        raise HTTPException(status_code=404, detail="Thread not found")
    return a


@api.post("/v1/assistants/{assistant_id}", response_model=assistants.AssistantRead, tags=['Assistants'])
def modify_assistant(assistant_id: str, assistant: assistants.AssistantModify):
    return assistants.modify(id=assistant_id, assistant=assistant)


@api.delete("/v1/assistants/{assistant_id}", tags=['Assistants'])
def delete_assistant(assistant_id: str):
    return assistants.delete(id=assistant_id)


@api.get("/v1/assistants", response_model=ListModel, tags=['Assistants'])
def list_assistants(limit: int = 20, order: str = "desc", after: str = None, before: str = None):
    return assistants.list(limit=limit, order=order, after=after, before=before)

# Threads


@api.post("/v1/threads", response_model=threads.ThreadRead, tags=['Threads'])
def create_thread(thread: threads.ThreadCreate):
    r = threads.create(thread=thread)
    return r


@api.get("/v1/threads/{thread_id}", response_model=threads.ThreadRead, tags=['Threads'])
def retrieve_thread(thread_id: str):
    t = threads.get(id=thread_id)
    if not t:
        raise HTTPException(status_code=404, detail="Thread not found")
    return t


@api.post("/v1/threads/{thread_id}", response_model=threads.ThreadRead, tags=['Threads'])
def modify_thread(thread_id: str, thread: threads.ThreadModify):
    return threads.modify(id=thread_id, thread=thread)


@api.delete("/v1/threads/{thread_id}", tags=['Threads'])
def delete_thread(thread_id: str):
    return threads.delete(id=thread_id)


@api.get("/v1/threads", response_model=ListModel, tags=['Threads'])
def list_threads(limit: int = 20, order: str = "desc", after: str = None, before: str = None):
    return threads.list(limit=limit, order=order, after=after, before=before)

# Messages


@api.post("/v1/threads/{thread_id}/messages", response_model=messages.MessageRead, tags=['Threads'])
def create_message(thread_id: str, message: messages.MessageCreate):
    r = messages.create(thread_id=thread_id, message=message)
    return r


@api.get("/v1/threads/{thread_id}/messages/{message_id}", response_model=messages.MessageRead, tags=['Threads'])
def retrieve_message(thread_id: str, message_id: str):
    t = messages.get(id=message_id)
    if not t:
        raise HTTPException(status_code=404, detail="Thread not found")
    return t


@api.post("/v1/threads/{thread_id}/messages/{message_id}", response_model=messages.MessageRead, tags=['Threads'])
def modify_message(thread_id: str, message_id: str, message: messages.MessageModify):
    return messages.modify(id=message_id, message=message)


@api.delete("/v1/threads/{thread_id}/messages/{message_id}", tags=['Threads'])
def delete_message(thread_id: str, message_id: str):
    return messages.delete(id=message_id)


@api.get("/v1/threads/{thread_id}/messages", response_model=messages.MessageList, tags=['Threads'])
def list_messages(thread_id: str, limit: int = 20, order: str = "desc", after: str = None, before: str = None):
    return messages.list(thread_id=thread_id, limit=limit, order=order, after=after, before=before)

# Runs


@api.post("/v1/threads/{thread_id}/runs", response_model=runs.RunRead, tags=['Runs'])
def create_run(thread_id: str, run: runs.RunCreate):
    r = runs.create(thread_id=thread_id, run=run)
    return r


@api.get("/v1/threads/{thread_id}/runs/{run_id}", response_model=runs.RunRead, tags=['Runs'])
def retrieve_run(thread_id: str, run_id: str):
    t = runs.get(thread_id=thread_id, run_id=run_id)
    if not t:
        raise HTTPException(status_code=404, detail="Run not found")
    return t


@api.post("/v1/threads/{thread_id}/runs/{run_id}", response_model=runs.RunRead, tags=['Runs'])
def modify_run(thread_id: str, run_id: str, run: runs.RunModify):
    return runs.modify(id=run_id, run=run)


@api.delete("/v1/threads/{thread_id}/runs/{run_id}", tags=['Runs'])
def delete_message(thread_id: str, run_id: str):
    return runs.delete(id=run_id)


@api.get("/v1/threads/{thread_id}/runs", response_model=ListModel, tags=['Runs'])
def list_runs(thread_id: str, limit: int = 20, order: str = "desc", after: str = None, before: str = None):
    return runs.list(thread_id=thread_id, limit=limit, order=order, after=after, before=before)

@api.post("/v1/threads/{thread_id}/runs/{run_id}/cancel", response_model=runs.RunRead, tags=['Runs'])
def cancel_run(thread_id: str, run_id: str):
    return runs.cancel(thread_id=thread_id, run_id=run_id)

@api.post("/v1/threads/runs", response_model=runs.RunRead, tags=['Runs'])
def create_thread_and_run(thread_run: runs.ThreadRunCreate):
    return runs.create_thread_and_run(thread_run=thread_run)

@api.get("/v1/threads/{thread_id}/runs/{run_id}/steps/{step_id}", response_model=runs.RunStep, tags=['Runs'])
def retrieve_run_step(thread_id: str, run_id: str, step_id: str):
    return runs.get_step(thread_id=thread_id, run_id=run_id, step_id=step_id)

@api.get("/v1/threads/{thread_id}/runs/{run_id}/steps", response_model=ListModel, tags=['Runs'])
def list_run_steps(thread_id: str, run_id: str):
    return runs.list_steps(thread_id=thread_id, run_id=run_id)

@api.get("/v1/threads/{thread_id}/runs/{run_id}/stream", tags=['Runs'])
async def get_message_stream(thread_id:str, run_id:str):
    iter = get_run_iter(run_id=run_id)
    #iter = create_run_iter(run_id=run_id)
    #for i in range(10):
    #    await iter.put(str(i))

    async def aiter():
        if not iter:
            return
    
        async for c in iter:
            if isinstance(c, str):
                e = {
                    "c": c
                }
                yield "event: message\ndata: %s\n\n" % json.dumps(e)
            elif isinstance(c, Exception):
                yield "event: error\ndata: %s\n\n" % json.dumps({"e": str(c)})
    return StreamingResponse(aiter(), headers={'Content-Type': "text/event-stream"})

@api.post("/hooks/{hook_name}/before", tags=["Hooks"])
async def execute_tool(hook_name:str, messages: List[dict]):
    h = tools.get_tool(hook_name)
    if not h or not isinstance(h, hook.Hook):
        raise HTTPException(status_code=404, detail="Hook not found")
    
    messages, args, metadata = await h.before(messages)

    return {
        "messages": messages,
        "args": args,
        "metadata": metadata
    }