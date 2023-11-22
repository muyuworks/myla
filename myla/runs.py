from typing import List, Dict, Any, Optional, Union
from sqlmodel import Field, Session, Column, JSON, select
from pydantic import BaseModel
from ._models import auto_session, DeletionStatus, MetadataModel, ReadModel, DBModel, ListModel
from ._models import create as create_model
from . import assistants

class RunEdit(MetadataModel):
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

class RunRead(ReadModel, RunBase):
    file_ids: Optional[List[str]]

class Run(DBModel, RunBase, table=True):
    """
    Represents an assistant that can call the model and use tools.
    """
    

class ThreadRunCreate(MetadataModel):
    assistant_id: str
    thread: Optional[Dict]
    model: Optional[str]
    instructions: Optional[str]
    tools: Optional[List[Dict]]
    file_ids: Optional[List[str]]

class RunStep(DBModel, MetadataModel):
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


def create(thread_id: str, run: RunCreate, session: Session = None) -> RunRead:
    db_model = Run.from_orm(run)
    db_model.thread_id = thread_id
    db_model.status = "queued"

    dbo = create_model(object="thread.run",
                       meta_model=run, db_model=db_model)

    r = RunRead(**dbo.dict())
    r.metadata = dbo.metadata_

    return r


@auto_session
def get(thread_id:str, run_id: str, session: Session = None) -> Union[RunRead, None]:
    r = None
    dbo = session.get(Run, run_id)
    if dbo:
        
        d = dbo.dict()

        # Get thread
        # Get assistant
        assitant = assistants.get(id=dbo.assistant_id, session=session)
        
        d.update(assitant.dict())

        r = RunRead(**d)
        r.metadata = dbo.metadata_
    return r


@auto_session
def modify(id: str, run: RunModify, session: Session = None) -> Union[RunRead, None]:
    r = None

    dbo = session.get(Run, id)
    if dbo:
        for k, v in run.dict(exclude_unset=True).items():
            
            if k == 'metadata':
                dbo.metadata_ = v
            else:
                setattr(dbo, k, v)
            
        session.add(dbo)
        session.commit()
        session.refresh(dbo)

        # Get thread
        # Get assistant
        #asistant = assistants.get(id=dbo.assistant_id, session=session)
        
        r = RunRead(**dbo.dict())
        r.metadata = dbo.metadata_

    return r


@auto_session
def delete(id: str, session: Optional[Session] = None) -> DeletionStatus:
    dbo = session.get(Run, id)
    if dbo:
        session.delete(dbo)
        session.commit()
    return DeletionStatus(id=id, object="thread.run.deleted", deleted=True)

@auto_session
def list(thread_id:str, limit: int = 20, order: str = "desc", after:str = None, before:str = None, session: Optional[Session] = None) -> ListModel:
    select_stmt = select(Run)

    select_stmt = select_stmt.order_by(-Run.created_at if order == "desc" else Run.created_at)
    if after:
        select_stmt = select_stmt.filter(Run.id > after)
    if before:
        select_stmt = select_stmt.filter(Run.id < before)

    select_stmt = select_stmt.limit(limit)
    
    dbos = session.exec(select_stmt).all()
    rs = []
    for dbo in dbos:
        
        # Get assistant
        #asistant = assistants.get(id=dbo.assistant_id, session=session)
        #if assitant:
        #    d.update(assitant.dict())

        a = RunRead(**dbo.dict())
        a.metadata = dbo.metadata_
        rs.append(a)
    r = ListModel(data=rs)
    return r

def cancel(thread_id: str, run_id: str, session: Session = None) -> Union[RunRead, None]:
    return

def create_thread_and_run(thread_run: ThreadRunCreate, session: Session = None) -> Union[RunRead, None]:
    return None

def create_step(run_id: str, step: RunStep, session: Session = None) -> Union[RunStep, None]:
    
    return None

def list_steps(thread_id: str, run_id: str, session: Session = None) -> ListModel:
    return ListModel(object="thread.run.step", data=[])

def get_step(thread_id: str, run_id: str, step_id: str, session: Session = None) -> Union[RunStep, None]:
    return None

@auto_session
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