import os
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel
from sqlmodel import JSON, Column, Field, Session

from . import _models


class AssistantBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    model: str
    instructions: Optional[str] = None
    tools: Optional[List[Dict[str, Any]]] = Field(sa_type=JSON, default=None)
    file_ids: Optional[List[str]] = Field(sa_type=JSON, default=None)


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
    db_model = Assistant.model_validate(assistant)
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
    return _models.modify(db_cls=Assistant, read_cls=AssistantRead, id=id, to_update=assistant.model_dump(exclude_unset=True), user_id=user_id, session=session)


@_models.auto_session
def delete(id: str, user_id: str = None, mode="soft", session: Optional[Session] = None) -> _models.DeletionStatus:
    return _models.delete(db_cls=Assistant, id=id, user_id=user_id, mode=mode, session=session)


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
