from typing import Dict, List, Optional, Union

from pydantic import BaseModel
from sqlmodel import JSON, Field, Session, select

from . import _models


class MessageText(BaseModel):
    value: str


class MessageContent(BaseModel):
    type: str
    text: Optional[List[MessageText]]


class MessageCreate(_models.MetadataModel):
    role: str
    content: str
    file_ids: Optional[List[str]] = None


class MessageModify(_models.MetadataModel):
    pass


class MessageRead(_models.ReadModel):
    thread_id: str
    assistant_id: Optional[str] = None
    run_id: Optional[str] = None
    role: Optional[str] = None
    content: Optional[List[MessageContent]] = None
    file_ids: Optional[List[str]] = []


class MessageList(_models.ListModel):
    data: List[MessageRead]


class Message(_models.DBModel, table=True):
    """
    Represents an assistant that can call the model and use tools.
    """
    thread_id: Optional[str] = Field(index=True, default=None)
    assistant_id: Optional[str] = Field(index=True, nullable=True, default=None)
    run_id: Optional[str] = Field(index=True, nullable=True, default=None)
    role: str
    content: List[Dict] = Field(sa_type=JSON)
    file_ids: Optional[List[str]] = Field(sa_type=JSON, default=None)


@_models.auto_session
def create(
    thread_id: str,
    message: MessageCreate,
    assistant_id: Optional[str] = None,
    run_id: Optional[str] = None,
    tag: Optional[str] = None,
    user_id: Optional[str] = None,
    org_id: Optional[str] = None,
    session: Session = None
) -> MessageRead:
    db_model = Message(
        thread_id=thread_id,
        role=message.role,
        content=[
            MessageContent(type="text", text=[MessageText(value=message.content)]).model_dump()
        ],
        assistant_id=assistant_id,
        run_id=run_id
    )

    dbo = _models.create(
        object="thread.message",
        meta_model=message,
        db_model=db_model,
        tag=tag,
        user_id=user_id,
        org_id=org_id,
        session=session
    )
    return dbo.to_read(MessageRead)


@_models.auto_session
def get(id: str, thread_id: str = None, user_id: str = None, session: Session = None) -> Union[MessageRead, None]:
    r = _models.get(db_cls=Message, read_cls=MessageRead, id=id, user_id=None, session=session)
    if not r:
        return None

    if thread_id is not None and thread_id != r.thread_id:
        return None

    #if thread_id is not None:
    #    thread = threads.get(id=thread_id, user_id=user_id, session=session)
    #    if not thread:
    #        return None

    return r


@_models.auto_session
def modify(id: str, message: MessageModify, thread_id: str = None, user_id: str = None, session: Session = None) -> Union[MessageRead, None]:
    if thread_id is not None:
        msg = get(id=id, thread_id=thread_id, user_id=user_id, session=session)
        if not msg:
            return None
    return _models.modify(db_cls=Message, read_cls=MessageRead, id=id, to_update=message.model_dump(exclude_unset=True), user_id=user_id, session=session)


@_models.auto_session
def delete(id: str, thread_id: str = None, user_id: str = None, mode="soft", session: Optional[Session] = None) -> _models.DeletionStatus:
    if thread_id is not None:
        msg = get(id=id, thread_id=thread_id, user_id=user_id, session=session)
        if not msg:
            return None
    return _models.delete(db_cls=Message, id=id, user_id=user_id, mode=mode, session=session)


@_models.auto_session
def list(
    thread_id: str,
    limit: Optional[int] = 20,
    order: Optional[str] = "desc",
    after: Optional[str] = None,
    before: Optional[str] = None,
    tag: Optional[str] = None,
    user_id: Optional[str] = None,
    session: Session = None
) -> MessageList:
    #if user_id is not None:
    #    thread = threads.get(id=thread_id, user_id=user_id, session=session)
    #    if not thread:
    #        return MessageList(data=[])

    select_stmt = select(Message)
    select_stmt = select_stmt.filter(Message.is_deleted == False)
    select_stmt = select_stmt.where(Message.thread_id == thread_id)

    select_stmt = select_stmt.order_by(-Message.created_at if order == "desc" else Message.created_at)
    if after:
        m = get(id=after, thread_id=thread_id, user_id=user_id, session=session)
        if m:
            select_stmt = select_stmt.filter(Message.created_at > m.created_at)
    if before:
        m = get(id=before, thread_id=thread_id, user_id=user_id, session=session)
        if m:
            select_stmt = select_stmt.filter(Message.created_at < m.created_at)

    if tag:
        select_stmt = select_stmt.filter(Message.tag == tag)

    select_stmt = select_stmt.limit(limit)

    dbos = session.exec(select_stmt).all()
    rs = []
    for dbo in dbos:
        rs.append(dbo.to_read(MessageRead))
    r = MessageList(data=rs, first_id=rs[0].id if len(rs) > 0 else None, last_id=rs[-1].id if len(rs) > 0 else None)
    return r
