from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Column, JSON, Session, select
from .persistence import Persistence
from . import utils


class MetadataModel(BaseModel):
    """Represents an object that has metadata."""
    metadata: Optional[Dict[str, Any]]


class ReadModel(MetadataModel):
    """Represents an object with read-only attributes."""
    id: str
    object: str
    created_at: int


class DBModel(SQLModel):
    """Represents an object stored in database."""
    id: Optional[str] = Field(primary_key=True)
    object: Optional[str]
    created_at: Optional[int] = Field(index=True)
    metadata_: Optional[Dict[str, Any]] = Field(sa_column=Column(JSON))
    org_id: Optional[str] = Field(index=True)
    user_id: Optional[str] = Field(index=True)
    is_deleted: Optional[bool] = Field(index=True, default=False)
    deleted_at: Optional[int]

    def to_read(self, read_cls: ReadModel) -> ReadModel:
        r = read_cls(**self.dict())
        r.metadata = self.metadata_
        return r


class DeletionStatus(BaseModel):
    """Represents an object that represents the result of a deletion."""
    id: str
    object: str
    deleted: bool


class ListModel(BaseModel):
    """Represents a list of objects that represent the results of a data query."""
    object: str = "list"
    data: List[Any] = []
    first_id: Optional[str]
    last_id: Optional[str]
    has_more: bool = False


def auto_session(func):
    def inner(session: Optional[Session] = None, **kwargs):
        ss = session if session else Persistence.default().create_session()
        try:
            return func(session=ss, **kwargs)
        finally:
            if not session:
                ss.close()
    return inner


@auto_session
def create(object: str, meta_model: MetadataModel, db_model: DBModel, id: str = None, user_id: str = None, org_id: str = None, session: Session = None, auto_commit=True):
    id = id if id else utils.random_id()

    if object == "secret_key":
        id = "sk-" + id
    elif object == "assistant":
        id = "asst_" + id
    elif object == "thread":
        id = "thread_" + id
    elif object ==  "thread.message":
        id = "msg_" + id
    elif object == "thread.run":
        id = "run_" + id
    elif object == "thread.run.step":
        id = "step_" + id
    elif object == "organization":
        id = "org-" + id
    elif object == "user":
        id = "user-" + id

    db_model.id = id
    db_model.created_at = int(round(datetime.now().timestamp()))
    db_model.object = object
    db_model.metadata_ = meta_model.metadata
    db_model.user_id = user_id
    db_model.org_id = org_id

    session.add(db_model)
    if auto_commit:
        session.commit()
        session.refresh(db_model)

    return db_model


@auto_session
def list(db_cls: DBModel,
         read_cls: ReadModel,
         list_cls: ListModel,
         limit: int = 20,
         order: str = "desc",
         after: str = None,
         before: str = None,
         user_id: str = None,
         org_id: str = None,
         session: Optional[Session] = None
    ) -> ListModel:
    select_stmt = select(db_cls)

    select_stmt = select_stmt.order_by(-db_cls.created_at if order == "desc" else db_cls.created_at)
    if after:
        select_stmt = select_stmt.filter(db_cls.id > after)
    if before:
        select_stmt = select_stmt.filter(db_cls.id < before)

    if user_id:
        select_stmt = select_stmt.filter(db_cls.user_id == user_id)
    if org_id:
        select_stmt = select_stmt.filter(db_cls.org_id == org_id)

    select_stmt = select_stmt.limit(limit)

    dbos = session.exec(select_stmt).all()
    rs = []
    for dbo in dbos:
        rs.append(dbo.to_read(read_cls))
    return list_cls(data=rs)
