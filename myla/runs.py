from typing import List, Dict, Any, Optional, Union
from sqlmodel import Field, Session, Column, JSON, select
from pydantic import BaseModel
from . import _models
from . import threads


class RunEdit(_models.MetadataModel):
    pass


class RunCreate(RunEdit):
    assistant_id: str
    model: Optional[str]
    instructions: Optional[str]
    tools: Optional[List[Dict[str, Any]]] = []


class RunModify(RunEdit):
    pass


class RunBase(BaseModel):
    thread_id: Optional[str] = Field(index=True)
    assistant_id: str = Field(index=True)
    model: Optional[str]
    instructions: Optional[str]
    tools: Optional[List[Dict]] = Field(sa_column=Column(JSON))
    status: Optional[str] = Field(index=True, nullable=True)
    required_action: Optional[Dict] = Field(sa_column=Column(JSON))
    last_error: Optional[Dict] = Field(sa_column=Column(JSON))
    expires_at: Optional[int]
    started_at: Optional[int]
    failed_at: Optional[int]
    completed_at: Optional[int]


class RunRead(_models.ReadModel, RunBase):
    file_ids: Optional[List[str]]


class RunList(_models.ListModel):
    data: List[RunRead] = []


class Run(_models.DBModel, RunBase, table=True):
    """
    Represents an assistant that can call the model and use tools.
    """


class ThreadRunCreate(_models.MetadataModel):
    assistant_id: str
    thread: Optional[Dict]
    model: Optional[str]
    instructions: Optional[str]
    tools: Optional[List[Dict]]
    file_ids: Optional[List[str]]


class RunStep(_models.DBModel, _models.MetadataModel):
    assistant_id: str = Field(index=True)
    thread_id: str = Field(index=True)
    run_id: str = Field(index=True)
    type: str
    status: str
    step_details: Dict
    last_error: Optional[Dict]
    expired_at: Optional[int]
    cancelled_at: Optional[int]
    failed_at: Optional[int]
    completed_at: Optional[int]


@_models.auto_session
def create(thread_id: str, run: RunCreate, user_id: str = None, session: Session = None) -> Union[RunRead, None]:
    thread = threads.get(id=thread_id, user_id=user_id, session=session)
    if not thread:
        return None

    db_model = Run.from_orm(run)
    db_model.thread_id = thread_id
    db_model.status = "queued"

    dbo = _models.create(object="thread.run", meta_model=run, db_model=db_model, user_id=user_id, session=session)

    return dbo.to_read(RunRead)


@_models.auto_session
def get(thread_id: str, run_id: str, user_id: str = None, session: Session = None) -> Union[RunRead, None]:
    r = _models.get(db_cls=Run, read_cls=RunRead, id=run_id, user_id=user_id, session=session)
    if r.thread_id != thread_id:
        return None
    return r


@_models.auto_session
def modify(id: str, run: RunModify, user_id: str = None, session: Session = None) -> Union[RunRead, None]:
    return _models.modify(db_cls=Run, read_cls=RunRead, id=id, to_update=run.dict(exclude_unset=True), user_id=user_id, session=session)


@_models.auto_session
def delete(id: str, user_id: str = None, session: Optional[Session] = None) -> _models.DeletionStatus:
    return _models.delete(db_cls=Run, id=id, user_id=user_id, session=session)


@_models.auto_session
def list(
        thread_id: str,
        limit: int = 20,
        order: str = "desc",
        after: str = None,
        before: str = None,
        user_id: str = None,
        org_id: str = None,
        session: Optional[Session] = None
    ) -> RunList:
    select_stmt = select(Run)

    if thread_id:
        select_stmt = select_stmt.filter(Run.thread_id == thread_id)

    select_stmt = select_stmt.order_by(-Run.created_at if order == "desc" else Run.created_at)

    if after:
        select_stmt = select_stmt.filter(Run.id > after)
    if before:
        select_stmt = select_stmt.filter(Run.id < before)

    if user_id:
        select_stmt = select_stmt.filter(Run.user_id == user_id)
    if org_id:
        select_stmt = select_stmt.filter(Run.org_id == org_id)

    select_stmt = select_stmt.limit(limit)

    dbos = session.exec(select_stmt).all()

    rs = []
    for dbo in dbos:
        rs.append(dbo.to_read(RunRead))
    return RunList(data=rs, first_id=rs[0].id if len(rs) > 0 else None, last_id=rs[-1].id if len(rs) > 0 else None)


def cancel(thread_id: str, run_id: str, session: Session = None) -> Union[RunRead, None]:
    return


def create_thread_and_run(thread_run: ThreadRunCreate, session: Session = None) -> Union[RunRead, None]:
    return None


def create_step(run_id: str, step: RunStep, session: Session = None) -> Union[RunStep, None]:

    return None


def list_steps(thread_id: str, run_id: str, session: Session = None) -> _models.ListModel:
    return _models.ListModel(object="thread.run.step", data=[])


def get_step(thread_id: str, run_id: str, step_id: str, session: Session = None) -> Union[RunStep, None]:
    return None


@_models.auto_session
def update(id: str, session: Session = None, **kwargs):
    dbo = session.get(Run, id)
    if dbo:
        for k, v in kwargs.items():

            if k == 'metadata':
                dbo.metadata_ = v
            else:
                setattr(dbo, k, v)

        session.add(dbo)
        session.commit()
        session.refresh(dbo)
