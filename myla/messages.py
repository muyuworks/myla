import json
from typing import List, Dict, Any, Optional, Union
from sqlmodel import Field, Session, Column, JSON, select
from pydantic import BaseModel
from ._models import auto_session, DeletionStatus, MetadataModel, ReadModel, DBModel, ListModel
from ._models import create as create_model

class MessageText(BaseModel):
    value: str

class MessageContent(BaseModel):
    type: str
    text: Optional[List[MessageText]]

class MessageCreate(MetadataModel):
    role: str
    content: str
    file_ids: Optional[List[str]] = Field(sa_column=Column(JSON))

class MessageModify(MetadataModel):
    pass

class MessageRead(ReadModel):
    thread_id: str
    assistant_id: Optional[str]
    run_id: Optional[str]
    role: Optional[str]
    content: Optional[List[MessageContent]]
    file_ids: Optional[List[str]] = []

class MessageList(ListModel):
    data: List[MessageRead]

class Message(DBModel, table=True):
    """
    Represents an assistant that can call the model and use tools.
    """
    thread_id: Optional[str] = Field(index=True)
    assistant_id: Optional[str] = Field(index=True, nullable=True)
    run_id: Optional[str] = Field(index=True, nullable=True)
    role: str
    content: List[Dict] = Field(sa_column=Column(JSON))
    file_ids: Optional[List[str]] = Field(sa_column=Column(JSON))


def create(thread_id: str, message: MessageCreate, assistant_id:str = None, run_id:str=None, session: Session = None) -> MessageRead:
    db_model = Message(
        thread_id=thread_id,
        role=message.role,
        content=[
            MessageContent(type="text", text=[MessageText(value=message.content)]).dict()
        ],
        assistant_id=assistant_id,
        run_id=run_id
    )

    dbo = create_model(object="thread.message",
                       meta_model=message, db_model=db_model)
    r = MessageRead(**dbo.dict())
    r.metadata = dbo.metadata_
    return r


@auto_session
def get(id: str, session: Session = None) -> Union[MessageRead, None]:
    r = None
    dbo = session.get(Message, id)
    if dbo:
        r = MessageRead(**dbo.dict())
        r.metadata = dbo.metadata_

    return r


@auto_session
def modify(id: str, message: MessageModify, session: Session = None):
    r = None

    dbo = session.get(Message, id)
    if dbo:
        for k, v in message.dict(exclude_unset=True).items():
            if k == 'metadata':
                dbo.metadata_ = v
            else:
                setattr(dbo, k, v)

        session.add(dbo)
        session.commit()
        session.refresh(dbo)

        r = MessageRead(**dbo.dict())
        r.metadata = dbo.metadata_

    return r


@auto_session
def delete(id: str, session: Optional[Session] = None) -> DeletionStatus:
    dbo = session.get(Message, id)
    if dbo:
        session.delete(dbo)
        session.commit()
    return DeletionStatus(id=id, object="thread.message.deleted", deleted=True)

@auto_session
def list(thread_id: str, limit: int = 20, order: str = "desc", after:str = None, before:str = None, session: Optional[Session] = None) -> MessageList:
    select_stmt = select(Message)
    select_stmt = select_stmt.where(Message.thread_id == thread_id)

    select_stmt = select_stmt.order_by(-Message.created_at if order == "desc" else Message.created_at)
    if after:
        select_stmt = select_stmt.filter(Message.id > after)
    if before:
        select_stmt = select_stmt.filter(Message.id < before)

    select_stmt = select_stmt.limit(limit)
    
    dbos = session.exec(select_stmt).all()
    rs = []
    for dbo in dbos:
        a = MessageRead(**dbo.dict())
        a.metadata = dbo.metadata_
        rs.append(a)
    r = MessageList(data=rs, first_id=rs[0].id if len(rs) > 0 else None, last_id=rs[-1].id if len(rs) > 0 else None)
    return r