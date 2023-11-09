from typing import List
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from .persistence import Persistence
from sqlmodel import Session

from ._models import DeletionStatus, ListModel
from . import assistants, threads, messages, runs

API_VERSION = "v1"


@asynccontextmanager
async def lifespan(api: FastAPI):
    # on startup
    Persistence.default().initialize_database()
    yield
    # on shutdown
    pass

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


@api.post("/v1/assistants", response_model=assistants.AssistantRead)
def create_assistant(assistant: assistants.AssistantCreate):
    r = assistants.create(assistant=assistant)
    return r


@api.get("/v1/assistants/{assistant_id}", response_model=assistants.AssistantRead)
def retrieve_assistant(assistant_id: str):
    a = assistants.get(id=assistant_id)
    if not a:
        raise HTTPException(status_code=404, detail="Thread not found")
    return a


@api.post("/v1/assistants/{assistant_id}", response_model=assistants.AssistantRead)
def modify_assistant(assistant_id: str, assistant: assistants.AssistantModify):
    return assistants.modify(id=assistant_id, assistant=assistant)


@api.delete("/v1/assistants/{assistant_id}")
def delete_assistant(assistant_id: str):
    return assistants.delete(id=assistant_id)


@api.get("/v1/assistants", response_model=ListModel)
def list_assistants(limit: int = 20, order: str = "desc", after: str = None, before: str = None):
    return assistants.list(limit=limit, order=order, after=after, before=before)

# Threads


@api.post("/v1/threads", response_model=threads.ThreadRead)
def create_thread(thread: threads.ThreadCreate):
    r = threads.create(thread=thread)
    return r


@api.get("/v1/threads/{thread_id}", response_model=threads.ThreadRead)
def retrieve_thread(thread_id: str):
    t = threads.get(id=thread_id)
    if not t:
        raise HTTPException(status_code=404, detail="Thread not found")
    return t


@api.post("/v1/threads/{thread_id}", response_model=threads.ThreadRead)
def modify_thread(thread_id: str, thread: threads.ThreadModify):
    return threads.modify(id=thread_id, thread=thread)


@api.delete("/v1/threads/{thread_id}")
def delete_thread(thread_id: str):
    return threads.delete(id=thread_id)


@api.get("/v1/threads", response_model=ListModel)
def list_threads(limit: int = 20, order: str = "desc", after: str = None, before: str = None):
    return threads.list(limit=limit, order=order, after=after, before=before)

# Messages


@api.post("/v1/threads/{thread_id}/messages", response_model=messages.MessageRead)
def create_message(thread_id: str, message: messages.MessageCreate):
    r = messages.create(thread_id=thread_id, message=message)
    return r


@api.get("/v1/threads/{thread_id}/messages/{message_id}", response_model=messages.MessageRead)
def retrieve_message(thread_id: str, message_id: str):
    t = messages.get(id=message_id)
    if not t:
        raise HTTPException(status_code=404, detail="Thread not found")
    return t


@api.post("/v1/threads/{thread_id}/messages/{message_id}", response_model=messages.MessageRead)
def modify_message(thread_id: str, message_id: str, message: messages.MessageModify):
    return messages.modify(id=message_id, message=message)


@api.delete("/v1/threads/{thread_id}/messages/{message_id}")
def delete_message(thread_id: str, message_id: str):
    return messages.delete(id=message_id)


@api.get("/v1/threads/{thread_id}/messages", response_model=ListModel)
def list_messages(thread_id: str, limit: int = 20, order: str = "desc", after: str = None, before: str = None):
    return messages.list(thread_id=thread_id, limit=limit, order=order, after=after, before=before)

# Runs


@api.post("/v1/threads/{thread_id}/runs", response_model=runs.RunRead)
def create_run(thread_id: str, run: runs.RunCreate):
    r = runs.create(thread_id=thread_id, run=run)
    return r


@api.get("/v1/threads/{thread_id}/runs/{run_id}", response_model=runs.RunRead)
def retrieve_run(thread_id: str, run_id: str):
    t = runs.get(thread_id=thread_id, run_id=run_id)
    if not t:
        raise HTTPException(status_code=404, detail="Run not found")
    return t


@api.post("/v1/threads/{thread_id}/runs/{run_id}", response_model=runs.RunRead)
def modify_run(thread_id: str, run_id: str, run: runs.RunModify):
    return runs.modify(id=run_id, run=run)


@api.delete("/v1/threads/{thread_id}/runs/{run_id}")
def delete_message(thread_id: str, run_id: str):
    return runs.delete(id=run_id)


@api.get("/v1/threads/{thread_id}/runs", response_model=ListModel)
def list_runs(thread_id: str, limit: int = 20, order: str = "desc", after: str = None, before: str = None):
    return runs.list(thread_id=thread_id, limit=limit, order=order, after=after, before=before)
