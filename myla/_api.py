import os
import json
import asyncio
from typing import List
from datetime import datetime
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse

from ._models import ListModel, DeletionStatus
from . import _tools, assistants, files, threads, messages, runs
from ._run_scheduler import RunScheduler
from . import tools
from ._logging import logger
from . import utils
from .vectorstores import load_vectorstore_from_file
from . import llms

API_VERSION = "v1"

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
    title="Myla API",
    version=API_VERSION,
    docs_url="/swagger",
    redoc_url='/docs'
)


class Version(BaseModel):
    version: str


@api.get('/version', response_model=Version)
async def get_version():
    return Version(version=API_VERSION)


@api.get("/v1/models")
async def list_models():
    return {
        'object': 'list',
        'data': list(llms.list_models().values())
    }

# Assistants


@api.post("/v1/assistants", response_model=assistants.AssistantRead, tags=['Assistants'])
async def create_assistant(assistant: assistants.AssistantCreate):
    r = assistants.create(assistant=assistant)
    return r


@api.get("/v1/assistants/{assistant_id}", response_model=assistants.AssistantRead, tags=['Assistants'])
async def retrieve_assistant(assistant_id: str):
    a = assistants.get(id=assistant_id)
    if not a:
        raise HTTPException(status_code=404, detail="Thread not found")
    return a


@api.post("/v1/assistants/{assistant_id}", response_model=assistants.AssistantRead, tags=['Assistants'])
async def modify_assistant(assistant_id: str, assistant: assistants.AssistantModify):
    return assistants.modify(id=assistant_id, assistant=assistant)


@api.delete("/v1/assistants/{assistant_id}", tags=['Assistants'])
async def delete_assistant(assistant_id: str):
    return assistants.delete(id=assistant_id)


@api.get("/v1/assistants", response_model=ListModel, tags=['Assistants'])
async def list_assistants(limit: int = 20, order: str = "desc", after: str = None, before: str = None):
    return assistants.list(limit=limit, order=order, after=after, before=before)

# Threads


@api.post("/v1/threads", response_model=threads.ThreadRead, tags=['Threads'])
async def create_thread(thread: threads.ThreadCreate):
    r = threads.create(thread=thread)
    return r


@api.get("/v1/threads/{thread_id}", response_model=threads.ThreadRead, tags=['Threads'])
async def retrieve_thread(thread_id: str):
    t = threads.get(id=thread_id)
    if not t:
        raise HTTPException(status_code=404, detail="Thread not found")
    return t


@api.post("/v1/threads/{thread_id}", response_model=threads.ThreadRead, tags=['Threads'])
async def modify_thread(thread_id: str, thread: threads.ThreadModify):
    return threads.modify(id=thread_id, thread=thread)


@api.delete("/v1/threads/{thread_id}", tags=['Threads'])
async def delete_thread(thread_id: str):
    return threads.delete(id=thread_id)


@api.get("/v1/threads", response_model=ListModel, tags=['Threads'])
async def list_threads(limit: int = 20, order: str = "desc", after: str = None, before: str = None):
    return threads.list(limit=limit, order=order, after=after, before=before)

# Messages


@api.post("/v1/threads/{thread_id}/messages", response_model=messages.MessageRead, tags=['Messages'])
async def create_message(thread_id: str, message: messages.MessageCreate):
    r = messages.create(thread_id=thread_id, message=message)
    return r


@api.get("/v1/threads/{thread_id}/messages/{message_id}", response_model=messages.MessageRead, tags=['Messages'])
async def retrieve_message(thread_id: str, message_id: str):
    t = messages.get(id=message_id)
    if not t:
        raise HTTPException(status_code=404, detail="Thread not found")
    return t


@api.post("/v1/threads/{thread_id}/messages/{message_id}", response_model=messages.MessageRead, tags=['Messages'])
async def modify_message(thread_id: str, message_id: str, message: messages.MessageModify):
    return messages.modify(id=message_id, message=message)


@api.delete("/v1/threads/{thread_id}/messages/{message_id}", tags=['Messages'])
async def delete_message(thread_id: str, message_id: str):
    return messages.delete(id=message_id)


@api.get("/v1/threads/{thread_id}/messages", response_model=messages.MessageList, tags=['Messages'])
async def list_messages(thread_id: str, limit: int = 20, order: str = "desc", after: str = None, before: str = None):
    return messages.list(thread_id=thread_id, limit=limit, order=order, after=after, before=before)

# Runs


@api.post("/v1/threads/{thread_id}/runs", tags=['Runs'])
async def create_run(thread_id: str, run: runs.RunCreate, stream: bool = False, timeout: int = 30):
    r = runs.create(thread_id=thread_id, run=run)

    # Submit run to run
    RunScheduler.default().submit_run(r)

    if stream:
        r = await create_run_stream(thread_id=thread_id, run_id=r.id, timeout=timeout)

    return r


@api.get("/v1/threads/{thread_id}/runs/{run_id}", response_model=runs.RunRead, tags=['Runs'])
async def retrieve_run(thread_id: str, run_id: str):
    t = runs.get(thread_id=thread_id, run_id=run_id)
    if not t:
        raise HTTPException(status_code=404, detail="Run not found")
    return t


@api.post("/v1/threads/{thread_id}/runs/{run_id}", response_model=runs.RunRead, tags=['Runs'])
async def modify_run(thread_id: str, run_id: str, run: runs.RunModify):
    return runs.modify(id=run_id, run=run)


@api.delete("/v1/threads/{thread_id}/runs/{run_id}", tags=['Runs'])
async def delete_run(thread_id: str, run_id: str):
    return runs.delete(id=run_id)


@api.get("/v1/threads/{thread_id}/runs", response_model=ListModel, tags=['Runs'])
async def list_runs(thread_id: str, limit: int = 20, order: str = "desc", after: str = None, before: str = None):
    return runs.list(thread_id=thread_id, limit=limit, order=order, after=after, before=before)


@api.post("/v1/threads/{thread_id}/runs/{run_id}/cancel", response_model=runs.RunRead, tags=['Runs'])
async def cancel_run(thread_id: str, run_id: str):
    return runs.cancel(thread_id=thread_id, run_id=run_id)


@api.post("/v1/threads/runs", response_model=runs.RunRead, tags=['Runs'])
async def create_thread_and_run(thread_run: runs.ThreadRunCreate):
    return runs.create_thread_and_run(thread_run=thread_run)


@api.get("/v1/threads/{thread_id}/runs/{run_id}/steps/{step_id}", response_model=runs.RunStep, tags=['Runs'])
async def retrieve_run_step(thread_id: str, run_id: str, step_id: str):
    return runs.get_step(thread_id=thread_id, run_id=run_id, step_id=step_id)


@api.get("/v1/threads/{thread_id}/runs/{run_id}/steps", response_model=ListModel, tags=['Runs'])
async def list_run_steps(thread_id: str, run_id: str):
    return runs.list_steps(thread_id=thread_id, run_id=run_id)


async def create_run_stream(thread_id: str, run_id: str, timeout=30):
    # waiting for scheduler
    begin = datetime.now().timestamp()
    while True:
        iter = await RunScheduler.default().get_run_iter(run_id=run_id)
        if not iter and datetime.now().timestamp() < begin + timeout:
            await asyncio.sleep(1)
            continue
        else:
            break

    async def aiter():
        if not iter:
            logger.debug(f"Scheduler timeout: thread_id={thread_id}, run_id={run_id}")
            yield "event: error\ndata: %s\n\n" % json.dumps({"e": "Timeout."})
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

# Tools


@api.get("/v1/tools", response_model=List[str], tags=['Tools'])
async def list_tools():
    tools = []
    for t in _tools.get_tools().keys():
        tools.append(t)
    return tools


@api.post("/v1/tools/{tool_name}/execute", tags=["Tools"], response_model=tools.Context)
async def execute_tool(tool_name: str, context: tools.Context):
    tool_instance = _tools.get_tool(tool_name)
    if not tool_instance or not isinstance(tool_instance, tools.Tool):
        raise HTTPException(status_code=404, detail="Tool not found")

    await tool_instance.execute(context=context)

    return context

# Files


@api.post("/v1/files", response_model=files.FileRead, tags=['Files'])
async def upload_file(request: Request, file: UploadFile):
    form = await request.form()
    purpose = form.get("purpose")
    if purpose != "assistants":
        raise HTTPException(status_code=400, detail="Invalid purpose. [assistants]")

    metadata = {}
    embeddings_columns = []
    loader = None
    for k, v in form.items():
        if k != "purpose" and k != "file":
            metadata[k] = v
            if k == 'embeddings':
                embeddings_columns = [i.strip() for i in v.split(',')]
            elif k == 'loader':
                loader = v

    file_upload = files.FileUpload(
        purpose=purpose,
        metadata=metadata
    )

    bytes = file.size
    filename = file.filename

    # Write file to disk
    data_dir = os.environ.get("DATA_DIR")
    if not data_dir:
        raise HTTPException(status_code=500, detail="DATA_DIR required.")
    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    files_dir = os.path.join(data_dir, "files")

    if not os.path.exists(files_dir):
        os.mkdir(files_dir)

    id = utils.sha1(utils.uuid())
    fname = os.path.join(files_dir, id)

    with open(fname, "wb") as f:
        read_bytes = None
        while True:
            read_bytes = await file.read(512)
            if read_bytes:
                f.write(read_bytes)
            else:
                break

    # Create a vectorstore loading task
    # TODO: background task and failover
    ftype = filename.split(".")[-1]

    if purpose == "assistants":
        logger.info(f"Build vectorstore: id={id}, ftype={ftype}")
        async def _vs_load_task():
            load_vectorstore_from_file(collection=id, fname=fname, ftype=ftype, embeddings_columns=embeddings_columns, loader=loader)
        try:
            await _vs_load_task()
        except Exception as e:
            logger.debug(f"Build vectorstore failed", exc_info=e)
            raise HTTPException(status_code=400, detail=f"Can't build vectorstore. {e}")

    return files.create(id=id, file=file_upload, bytes=bytes, filename=filename)


@api.get("/v1/files", response_model=files.FileList, tags=["Files"])
async def list_files(purpose: str = None, limit: int = 20, order: str = "desc", after: str = None, before: str = None) -> files.FileList:
    return files.list(purpose=purpose, limit=limit, order=order, after=after, before=before)


@api.get("/v1/files/{file_id}", response_model=files.FileRead, tags=['Files'])
async def retrieve_file(file_id: str):
    file = files.get(id=file_id)
    if not file:
        raise HTTPException(status_code=404, detail=f"File not found: {file_id}")
    return file


@api.delete("/v1/files/{file_id}", response_model=DeletionStatus, tags=['Files'])
async def delete_file(file_id: str):
    return files.delete(id=file_id)
