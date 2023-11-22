from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Column, JSON, Session
from .persistence import Persistence
from . import utils


class MetadataModel(BaseModel):
    metadata: Optional[Dict[str, Any]]


class ReadModel(MetadataModel):
    id: str
    object: str
    created_at: int


class DBModel(SQLModel):
    id: Optional[str] = Field(primary_key=True)
    object: Optional[str]
    created_at: Optional[int] = Field(index=True)
    metadata_: Optional[Dict[str, Any]] = Field(sa_column=Column(JSON))


class DeletionStatus(BaseModel):
    id: str
    object: str
    deleted: bool

class ListModel(BaseModel):
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
def create(object: str, meta_model: MetadataModel, db_model: DBModel, id: str = None, session: Session = None) -> ReadModel:
    db_model.id = id if id else utils.sha1(utils.uuid())
    db_model.created_at = int(round(datetime.now().timestamp()))
    db_model.object = object
    db_model.metadata_ = meta_model.metadata

    session.add(db_model)
    session.commit()
    session.refresh(db_model)

    return db_model