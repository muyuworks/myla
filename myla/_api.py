import asyncio
import json
import os
from datetime import datetime
from typing import List, Optional

import aiofiles
from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from starlette.authentication import requires

from . import (_tools, assistants, files, llms, messages, permissions, runs,
               threads, tools, users, utils)
from ._logging import logger
from ._models import DeletionStatus, ListModel
from ._run_scheduler import RunScheduler
from .vectorstores import load_vectorstore_from_file

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


def _delete_mode():
    mode = os.environ.get('MYLA_DELETE_MODE')
    if mode is not None and isinstance(mode, str) and mode.lower().strip() == 'soft':
        return 'soft'
    else:
        return 'hard'


class Version(BaseModel):
    version: str


class Headers(BaseModel):
    organization: Optional[str]
    project: Optional[str]


def get_headers(request: Request):
    return Headers(
        organization=request.headers.get('OpenAI-Organization'),
        project=request.headers.get('OpenAI-Project')
    )


def check_permission(
        resource_type: str,
        resource_id: str,
        org_id: str,
        project_id: str,
        owner_id: str,
        user_id: str,
        orgs: List[users.OrganizationRead],
        permission: str
    ) -> bool:
    r = permissions.check(resource_type, resource_id, org_id, project_id, owner_id, user_id, orgs, permission)
    if not r:
        raise HTTPException(status_code=403, detail=f"User {user_id} does not have permission {permission} on {resource_type} {resource_id}")


def check_resources_permission(resource_type, request, permission):
    headers = get_headers(request)

    check_permission(
        resource_type=resource_type,
        resource_id=None,
        org_id=headers.organization or request.user.primary_org_id,
        project_id=headers.project,
        owner_id=request.user.id,
        user_id=request.user.id,
        orgs=request.user.orgs,
        permission=permission
    )


def check_object_permission(obj, request, permission):
    check_permission(
        resource_type="/assistants",
        resource_id=obj.id,
        org_id=obj.org_id,
        project_id=None,
        owner_id=obj.user_id,
        user_id=request.user.id,
        orgs=request.user.orgs,
        permission=permission
    )


@api.get('/version', response_model=Version, tags=['System'])
@requires(['authenticated'])
async def get_version(request: Request):
    return Version(version=API_VERSION)


@api.get("/v1/models", tags=['System'])
@requires(['authenticated'])
async def list_models(request: Request):
    return {
        'object': 'list',
        'data': list(llms.list_models().values())
    }

# Assistants


@api.post("/v1/assistants", response_model=assistants.AssistantRead, tags=['Assistants'])
@requires(['authenticated'])
async def create_assistant(assistant: assistants.AssistantCreate, request: Request):
    check_resources_permission("assistants", request, "write")

    headers = get_headers(request)

    r = assistants.create(assistant=assistant, user_id=request.user.id, org_id=headers.organization or request.user.primary_org_id)
    return r


@ api.get("/v1/assistants/{assistant_id}", response_model=assistants.AssistantRead, tags=['Assistants'])
@ requires(['authenticated'])
async def retrieve_assistant(assistant_id: str, request: Request):
    a = assistants.get(id=assistant_id)
    if not a:
        raise HTTPException(status_code=404, detail="Assistant not found")

    check_object_permission(a, request, "read")

    return a


@ api.post("/v1/assistants/{assistant_id}", response_model=assistants.AssistantRead, tags=['Assistants'])
@ requires(['authenticated'])
async def modify_assistant(assistant_id: str, assistant: assistants.AssistantModify, request: Request):
    a = assistants.get(assistant_id)
    if not a:
        raise HTTPException(status_code=404, detail="Assistant not found")

    check_object_permission(a, request, "write")

    a = assistants.modify(id=assistant_id, assistant=assistant)
    return a


@ api.delete("/v1/assistants/{assistant_id}", tags=['Assistants'])
@ requires(['authenticated'])
async def delete_assistant(assistant_id: str, request: Request):
    a = assistants.get(assistant_id)
    if a is not None:
        check_object_permission(a, request, "write")
    return assistants.delete(id=assistant_id, mode=_delete_mode())


@ api.get("/v1/assistants", response_model=assistants.AssistantList, tags=['Assistants'])
@ requires(['authenticated'])
async def list_assistants(request: Request, limit: int = 20, order: str = "desc", after: str = None, before: str = None):
    headers = get_headers(request)

    check_resources_permission("assistants", request, "read")

    return assistants.list(limit=limit, order=order, after=after, before=before, org_id=headers.organization or request.user.primary_org_id)

# Threads


def check_thread_permission(thread_id, request, permission):
    t = threads.get(id=thread_id)
    if not t:
        raise HTTPException(status_code=404, detail="Thread not found")

    check_object_permission(t, request, permission)

    return t


@ api.post("/v1/threads", response_model=threads.ThreadRead, tags=['Threads'])
@ requires(['authenticated'])
async def create_thread(thread: threads.ThreadCreate, request: Request, tag: Optional[str] = None):
    headers = get_headers(request)

    check_resources_permission("threads", request, "write")

    r = threads.create(thread=thread, tag=tag, user_id=request.user.id, org_id=headers.organization or request.user.primary_org_id)
    return r


@ api.get("/v1/threads/{thread_id}", response_model=threads.ThreadRead, tags=['Threads'])
@ requires(['authenticated'])
async def retrieve_thread(thread_id: str, request: Request):
    t = check_thread_permission(thread_id, request, "read")

    return t


@ api.post("/v1/threads/{thread_id}", response_model=threads.ThreadRead, tags=['Threads'])
@ requires(['authenticated'])
async def modify_thread(thread_id: str, thread: threads.ThreadModify, request: Request):
    check_thread_permission(thread_id, request, "write")

    return threads.modify(id=thread_id, thread=thread)


@ api.delete("/v1/threads/{thread_id}", tags=['Threads'])
@ requires(['authenticated'])
async def delete_thread(thread_id: str, request: Request):
    t = threads.get(thread_id)
    if t is not None:
        check_object_permission(t, request, "write")
    return threads.delete(id=thread_id, mode=_delete_mode())


@ api.get("/v1/threads", response_model=threads.ThreadList, tags=['Threads'])
@ requires(['authenticated'])
async def list_threads(
    request: Request,
    limit: int = 20,
    order: str = "desc",
    after: Optional[str] = None,
    before: Optional[str] = None,
    tag: Optional[str] = None
):
    headers = get_headers(request)
    check_resources_permission("threads", request, "read")

    return threads.list(limit=limit, order=order, after=after, before=before, tag=tag, org_id=headers.organization or request.user.primary_org_id)


# Messages


@ api.post("/v1/threads/{thread_id}/messages", response_model=messages.MessageRead, tags=['Messages'])
@ requires(['authenticated'])
async def create_message(thread_id: str, message: messages.MessageCreate, request: Request, tag: Optional[str] = None):
    t = check_thread_permission(thread_id, request, "write")

    r = messages.create(thread_id=thread_id, message=message, tag=tag, user_id=request.user.id, org_id=t.org_id)
    return r


@ api.get("/v1/threads/{thread_id}/messages/{message_id}", response_model=messages.MessageRead, tags=['Messages'])
@ requires(['authenticated'])
async def retrieve_message(thread_id: str, message_id: str, request: Request):
    check_thread_permission(thread_id, request, "read")

    m = messages.get(id=message_id, thread_id=thread_id)
    if not m:
        raise HTTPException(status_code=404, detail="Message not found")

    check_object_permission(m, request, "read")

    return m


@ api.post("/v1/threads/{thread_id}/messages/{message_id}", response_model=messages.MessageRead, tags=['Messages'])
@ requires(['authenticated'])
async def modify_message(thread_id: str, message_id: str, message: messages.MessageModify, request: Request):
    check_thread_permission(thread_id, request, "write")

    m = messages.get(id=message_id, thread_id=thread_id)
    if not m:
        raise HTTPException(status_code=404, detail="Message not found")

    check_object_permission(m, request, "write")

    return messages.modify(id=message_id, message=message, thread_id=thread_id)


@ api.delete("/v1/threads/{thread_id}/messages/{message_id}", tags=['Messages'])
async def delete_message(thread_id: str, message_id: str, request: Request):
    check_thread_permission(thread_id, request, "write")

    m = messages.get(id=message_id, thread_id=thread_id)
    if m is not None:
        check_object_permission(m, request, "write")

    return messages.delete(id=message_id, thread_id=thread_id, user_id=request.user.id, mode=_delete_mode())


@ api.get("/v1/threads/{thread_id}/messages", response_model=messages.MessageList, tags=['Messages'])
@ requires(['authenticated'])
async def list_messages(
    request: Request,
    thread_id: str,
    limit: Optional[int] = 20,
    order: Optional[str] = "desc",
    after: Optional[str] = None,
    before: Optional[str] = None,
    tag: Optional[str] = None
):
    check_thread_permission(thread_id, request, "read")

    return messages.list(
        thread_id=thread_id,
        tag=tag,
        limit=limit,
        order=order,
        after=after,
        before=before
    )

# Runs


@api.post("/v1/threads/{thread_id}/runs", tags=['Runs'])
@requires(['authenticated'])
async def create_run(request: Request, thread_id: str, run: runs.RunCreate, stream: bool = False, timeout: int = 30):
    t = check_thread_permission(thread_id, request, "write")

    if stream:
        if run.metadata is None:
            run.metadata = {}
        run.metadata["stream"] = True

    r = runs.create(thread_id=thread_id, run=run, user_id=request.user.id, org_id=t.org_id)

    # Submit run to run
    if r.metadata is None:
        r.metadata = {}
    # r.metadata["user_id"] = request.user.id
    RunScheduler.default().submit_run(r)

    if stream:
        r = await create_run_stream(thread_id=thread_id, run_id=r.id, timeout=timeout)

    return r


@api.get("/v1/threads/{thread_id}/runs/{run_id}", response_model=runs.RunRead, tags=['Runs'])
@requires(['authenticated'])
async def retrieve_run(thread_id: str, run_id: str, request: Request):
    check_thread_permission(thread_id, request, "read")

    r = runs.get(thread_id=thread_id, run_id=run_id)
    if not r:
        raise HTTPException(status_code=404, detail="Run not found")
    return r


@api.post("/v1/threads/{thread_id}/runs/{run_id}", response_model=runs.RunRead, tags=['Runs'])
@requires(['authenticated'])
async def modify_run(thread_id: str, run_id: str, run: runs.RunModify, request: Request):
    # TODO: check files permissions
    check_thread_permission(thread_id, request, "write")

    r = runs.get(thread_id=thread_id, run_id=run_id)
    if not r:
        raise HTTPException(status_code=404, detail="Run not found")

    return runs.modify(id=run_id, run=run)


@api.delete("/v1/threads/{thread_id}/runs/{run_id}", tags=['Runs'])
@requires(['authenticated'])
async def delete_run(thread_id: str, run_id: str, request: Request):
    check_thread_permission(thread_id, request, "write")
    r = runs.get(thread_id=thread_id, run_id=run_id)
    if r is not None:
        check_object_permission(r, request, "write")

    return runs.delete(id=run_id, mode=_delete_mode())


@api.get("/v1/threads/{thread_id}/runs", response_model=runs.RunList, tags=['Runs'])
@requires(['authenticated'])
async def list_runs(request: Request, thread_id: str, limit: int = 20, order: str = "desc", after: str = None, before: str = None):
    check_thread_permission(thread_id, request, "read")
    return runs.list(thread_id=thread_id, limit=limit, order=order, after=after, before=before, user_id=request.user.id)


@api.post("/v1/threads/{thread_id}/runs/{run_id}/cancel", response_model=runs.RunRead, tags=['Runs'])
@requires(['authenticated'])
async def cancel_run(thread_id: str, run_id: str, request: Request):
    # TODO: check permissions
    return runs.cancel(thread_id=thread_id, run_id=run_id)


@api.post("/v1/threads/runs", response_model=runs.RunRead, tags=['Runs'])
@requires(['authenticated'])
async def create_thread_and_run(thread_run: runs.ThreadRunCreate, request: Request):
    # TODO: check permissions
    return runs.create_thread_and_run(thread_run=thread_run)


@api.get("/v1/threads/{thread_id}/runs/{run_id}/steps/{step_id}", response_model=runs.RunStep, tags=['Runs'])
@requires(['authenticated'])
async def retrieve_run_step(thread_id: str, run_id: str, step_id: str, request: Request):
    # TODO: check permissions
    return runs.get_step(thread_id=thread_id, run_id=run_id, step_id=step_id)


@api.get("/v1/threads/{thread_id}/runs/{run_id}/steps", response_model=ListModel, tags=['Runs'])
@requires(['authenticated'])
async def list_run_steps(thread_id: str, run_id: str, request: Request):
    # TODO: check permissions
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
@requires(['authenticated'])
async def list_tools(request: Request):
    tools = []
    for t in _tools.get_tools().keys():
        tools.append(t)
    return tools


@api.post("/v1/tools/{tool_name}/execute", tags=["Tools"], response_model=tools.Context)
@requires(['authenticated'])
async def execute_tool(tool_name: str, context: tools.Context, request: Request):
    tool_instance = _tools.get_tool(tool_name)
    if not tool_instance or not isinstance(tool_instance, tools.Tool):
        raise HTTPException(status_code=404, detail="Tool not found")

    await tool_instance.execute(context=context)

    return context

# Files


@api.post("/v1/files", response_model=files.FileRead, tags=['Files'])
@requires(['authenticated'])
async def upload_file(request: Request, file: UploadFile):
    headers = get_headers(request)

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

    id = "file-" + utils.random_id()
    fname = os.path.join(files_dir, id)

    async with aiofiles.open(fname, "wb") as f:
        read_bytes = None
        while True:
            read_bytes = await file.read(512)
            if read_bytes:
                await f.write(read_bytes)
            else:
                break

    # Create a vectorstore loading task
    # TODO: background task and failover
    ftype = filename.split(".")[-1]

    if purpose == "assistants":
        logger.info(f"Build vectorstore: id={id}, ftype={ftype}")
        try:
            def _load_vs():
                return load_vectorstore_from_file(
                    collection=id,
                    fname=fname,
                    ftype=ftype,
                    embeddings_columns=embeddings_columns,
                    loader=loader,
                    group_by=metadata.get('group_by'),
                    instruction=metadata.get('instruction'),
                    metadata=metadata
                )
            await asyncio.get_running_loop().run_in_executor(None, _load_vs)
        except Exception as e:
            logger.warn(f"Build vectorstore failed:", exc_info=e)
            raise HTTPException(status_code=400, detail=f"Can't build vectorstore. {e}")

    check_resources_permission("files", request, "write")
    return files.create(id=id, file=file_upload, bytes=bytes, filename=filename, user_id=request.user.id, org_id=headers.organization or request.user.primary_org_id)


@api.get("/v1/files", response_model=files.FileList, tags=["Files"])
@requires(['authenticated'])
async def list_files(request: Request, purpose: str = None, limit: int = 20, order: str = "desc", after: str = None, before: str = None) -> files.FileList:
    check_resources_permission("files", request, "read")
    headers = get_headers(request)
    return files.list(purpose=purpose, limit=limit, order=order, after=after, before=before, org_id=headers.organization or request.user.primary_org_id)


@api.get("/v1/files/{file_id}", response_model=files.FileRead, tags=['Files'])
@requires(['authenticated'])
async def retrieve_file(file_id: str, request: Request):
    file = files.get(id=file_id)
    if not file:
        raise HTTPException(status_code=404, detail=f"File not found: {file_id}")

    check_object_permission(file, request, "read")

    return file


@api.delete("/v1/files/{file_id}", response_model=DeletionStatus, tags=['Files'])
@requires(['authenticated'])
async def delete_file(file_id: str, request: Request):
    file = files.get(id=file_id)
    if file is not None:
        check_object_permission(file, request, "write")

    return files.delete(id=file_id, mode=_delete_mode())


@api.post("/v1/users/{username}/login", response_model=users.UserLoginResult, tags=['Users'])
async def login(username: str, user: users.UserLogin):
    if username != user.username:
        raise HTTPException(409, "username conflicted.")

    r = users.login(user=user)
    if not r:
        raise HTTPException(403)
    else:
        return r


class ChangePasswordReq(BaseModel):
    password: str


@api.put("/v1/users/{username}/password", response_model=users.UserRead, tags=['Users'])
@requires(['authenticated'])
async def change_password(username: str, password: ChangePasswordReq, request: Request) -> users.UserRead:
    # TODO: check username
    return users.change_password(user_id=request.user.id, new_password=password.password)


def check_sa(user_id):
    user = users.get_user(id=user_id)
    if not user.is_sa:
        raise HTTPException(status_code=403)


@api.get("/v1/users", response_model=users.UserList, tags=['Users'])
@requires(['authenticated'])
async def list_users(request: Request) -> users.UserList:
    check_sa(request.user.id)
    return users.list_users()


@api.post("/v1/users", response_model=users.UserRead, tags=['Users'])
@requires(['authenticated'])
async def create_user(user: users.UserCreate, request: Request) -> users.UserRead:
    check_sa(request.user.id)
    u = users.get_user_by_uername(username=user.username)
    if u:
        raise HTTPException(status_code=409, detail="User exists.")
    return users.create_user(user=user)


@api.delete("/v1/users/{username}", response_model=DeletionStatus, tags=['Users'])
@requires(['authenticated'])
async def delete_user(username: str, request: Request) -> DeletionStatus:
    check_sa(user_id=request.user.id)
    user = users.get_user_by_uername(username=username)
    if not user:
        raise HTTPException(status_code=404, detail='User not found.')

    if user.id == request.user.id:
        raise HTTPException(status_code=409, detail="Delete conflict.")
    return users.delete_user(id=user.id)


@api.get("/v1/secret_keys", response_model=users.SecrectKeyList, tags=['Users'])
@requires(['authenticated'])
async def list_secret_keys(request: Request) -> users.SecrectKeyList:
    sks = users.list_secret_keys(user_id=request.user.id)
    for i in range(len(sks.data)):
        sk = sks.data[i].id
        sk = 'sk-...' + sk[-4:]
        sks.data[i].id = sk
    return sks


@api.delete("/v1/secret_keys/{secret_key}", response_model=DeletionStatus, tags=['Users'])
@requires(['authenticated'])
async def delete_secret_key(secret_key: str, request: Request) -> DeletionStatus:
    try:
        return users.delete_secret_key(id=secret_key, user_id=request.user.id)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@api.post("/v1/secret_keys", response_model=users.SecretKeyRead, tags=['Users'])
@requires(['authenticated'])
async def create_secret_key(request: Request) -> users.SecretKeyRead:
    return users.create_secret_key(key=users.SecrectKeyCreate(), user_id=request.user.id)


@api.get("/v1/organizations", response_model=users.OrganizationList, tags=['Users'])
async def list_organizations(request: Request) -> users.OrganizationList:
    return users.list_orgs(user_id=request.user.id)


@api.get("/v1/organizations/{org_id}/members", tags=['Users'])
async def list_org_members(request: Request, org_id: str):
    headers = get_headers(request=request)

    if headers.organization != org_id:
        raise HTTPException(status_code=403, detail="You are not authorized to access this resource")

    check_resources_permission("members", request, "write")

    results = users.list_org_members(org_id=org_id)

    return {
        "object": "list",
        "data": [{"user": x[0].to_read(users.UserRead).model_dump(), "role": x[1].role} for x in results],
        "has_more": False,
    }


@api.post("/v1/organizations/{org_id}/members", tags=['Users'])
async def add_org_member(request: Request, org_id: str, member: users.OrgMemberCreate):
    headers = get_headers(request=request)

    if headers.organization != org_id:
        raise HTTPException(status_code=403, detail="You are not authorized to access this resource")

    check_resources_permission("members", request, "write")

    user = users.add_org_member(org_id=org_id, member=member)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user
