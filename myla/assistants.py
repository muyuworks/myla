import os
from typing import List, Dict, Any, Optional, Union
from sqlmodel import Field, Session, Column, JSON, select
from pydantic import BaseModel
from ._models import auto_session, DeletionStatus, MetadataModel, ReadModel, DBModel, ListModel
from ._models import create as create_model


class AssistantBase(BaseModel):
    name: Optional[str]
    description: Optional[str]
    model: str
    instructions: Optional[str]
    tools: Optional[List[Dict[str, Any]]] = Field(sa_column=Column(JSON))
    file_ids: Optional[List[str]] = Field(sa_column=Column(JSON))


class AssistantEdit(MetadataModel, AssistantBase):
    pass

class AssistantCreate(AssistantEdit):
    pass

class AssistantModify(AssistantEdit):
    pass

class AssistantRead(ReadModel, AssistantBase):
    pass


class Assistant(DBModel, AssistantBase, table=True):
    """
    Represents an assistant that can call the model and use tools.
    """
    pass


def create(assistant: AssistantCreate, session: Session = None) -> AssistantRead:
    db_model = Assistant.from_orm(assistant)
    if not db_model.model or db_model == '':
        default_model = os.environ.get("DEFAULT_LLM_MODEL_NAME")
        if default_model:
            db_model.model = default_model

    dbo = create_model(object="assistant",
                       meta_model=assistant, db_model=db_model)
    r = AssistantRead(**dbo.dict())
    r.metadata = dbo.metadata_
    return r


@auto_session
def get(id: str, session: Session = None) -> Union[AssistantRead, None]:
    r = None
    dbo = session.get(Assistant, id)
    if dbo:
        r = AssistantRead(**dbo.dict())
        r.metadata = dbo.metadata_

    return r


@auto_session
def modify(id: str, assistant: AssistantModify, session: Session = None):
    r = None

    dbo = session.get(Assistant, id)
    if dbo:
        for k, v in assistant.dict(exclude_unset=True).items():
            if k == 'metadata':
                dbo.metadata_ = v
            else:
                setattr(dbo, k, v)

        session.add(dbo)
        session.commit()
        session.refresh(dbo)

        r = AssistantRead(**dbo.dict())
        r.metadata = dbo.metadata_

    return r


@auto_session
def delete(id: str, session: Optional[Session] = None) -> DeletionStatus:
    dbo = session.get(Assistant, id)
    if dbo:
        session.delete(dbo)
        session.commit()
    return DeletionStatus(id=id, object="assistant.deleted", deleted=True)

@auto_session
def list(limit: int = 20, order: str = "desc", after:str = None, before:str = None, session: Optional[Session] = None) -> ListModel:
    select_stmt = select(Assistant)

    select_stmt = select_stmt.order_by(-Assistant.created_at if order == "desc" else Assistant.created_at)
    if after:
        select_stmt = select_stmt.filter(Assistant.id > after)
    if before:
        select_stmt = select_stmt.filter(Assistant.id < before)

    select_stmt = select_stmt.limit(limit)
    
    dbos = session.exec(select_stmt).all()
    rs = []
    for dbo in dbos:
        a = AssistantRead(**dbo.dict())
        a.metadata = dbo.metadata_
        rs.append(a)
    r = ListModel(data=rs)
    return r