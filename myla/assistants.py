import os
from typing import List, Dict, Any, Optional, Union
from sqlmodel import Field, Session, Column, JSON
from pydantic import BaseModel
from . import _models


class AssistantBase(BaseModel):
    name: Optional[str]
    description: Optional[str]
    model: str
    instructions: Optional[str]
    tools: Optional[List[Dict[str, Any]]] = Field(sa_column=Column(JSON))
    file_ids: Optional[List[str]] = Field(sa_column=Column(JSON))


class AssistantEdit(_models.MetadataModel, AssistantBase):
    pass


class AssistantCreate(AssistantEdit):
    pass


class AssistantModify(AssistantEdit):
    pass


class AssistantRead(_models.ReadModel, AssistantBase):
    pass


class AssistantList(_models.ListModel):
    data: List[AssistantRead] = []


class Assistant(_models.DBModel, AssistantBase, table=True):
    """
    Represents an assistant that can call the model and use tools.
    """


@_models.auto_session
def create(assistant: AssistantCreate, user_id: str = None, org_id: str = None, session: Session = None) -> AssistantRead:
    db_model = Assistant.from_orm(assistant)
    if not db_model.model or db_model == '':
        default_model = os.environ.get("DEFAULT_LLM_MODEL_NAME")
        if default_model:
            db_model.model = default_model

    dbo = _models.create(object="assistant", meta_model=assistant, db_model=db_model, user_id=user_id, org_id=org_id, session=session)
    return dbo.to_read(AssistantRead)


@_models.auto_session
def get(id: str, user_id: str = None, session: Session = None) -> Union[AssistantRead, None]:
    return _models.get(db_cls=Assistant, read_cls=AssistantRead, id=id, user_id=user_id, session=session)


@_models.auto_session
def modify(id: str, assistant: AssistantModify, user_id: str = None, session: Session = None) -> Union[AssistantRead, None]:
    return _models.modify(db_cls=Assistant, read_cls=AssistantRead, id=id, to_update=assistant.dict(exclude_unset=True), user_id=user_id, session=session)


@_models.auto_session
def delete(id: str, user_id: str = None, session: Optional[Session] = None) -> _models.DeletionStatus:
    return _models.delete(db_cls=Assistant, id=id, user_id=user_id, session=session)


@_models.auto_session
def list(
        limit: int = 20,
        order: str = "desc",
        after: str = None,
        before: str = None,
        user_id: str = None,
        org_id: str = None,
        session: Optional[Session] = None
    ) -> AssistantList:
    return _models.list(
        db_cls=Assistant,
        read_cls=AssistantRead,
        list_cls=AssistantList,
        limit=limit,
        order=order,
        after=after,
        before=before,
        user_id=user_id,
        org_id=org_id,
        session=session
    )
