from typing import Optional, Union, List
from sqlmodel import Session, select
from ._models import auto_session, DeletionStatus, MetadataModel, ReadModel, DBModel, ListModel
from ._models import create as create_model
from .messages import Message


class ThreadEdit(MetadataModel):
    # message list
    pass


class ThreadCreate(ThreadEdit):
    pass


class ThreadModify(ThreadEdit):
    pass


class ThreadRead(ReadModel):
    pass


class ThreadList(ListModel):
    data: List[ThreadRead] = []


class Thread(DBModel, table=True):
    """
    Represents an assistant that can call the model and use tools.
    """
    pass


@auto_session
def create(thread: ThreadEdit, user_id: str = None, org_id: str = None, session: Session = None) -> ThreadRead:
    db_model = Thread.from_orm(thread)
    dbo = create_model(object="thread", meta_model=thread, db_model=db_model, user_id=user_id, org_id=org_id, session=session)
    r = ThreadRead(**dbo.dict())
    r.metadata = dbo.metadata_
    return r


@auto_session
def get(id: str, session: Session = None) -> Union[ThreadRead, None]:
    r = None
    dbo = session.get(Thread, id)
    if dbo:
        r = ThreadRead(**dbo.dict())
        r.metadata = dbo.metadata_

    return r


@auto_session
def modify(id: str, thread: ThreadEdit, session: Session = None):
    r = None

    dbo = session.get(Thread, id)
    if dbo:
        for k, v in thread.dict(exclude_unset=True).items():
            if k == 'metadata':
                dbo.metadata_ = v
            else:
                setattr(dbo, k, v)

        session.add(dbo)
        session.commit()
        session.refresh(dbo)

        r = ThreadRead(**dbo.dict())
        r.metadata = dbo.metadata_

    return r


@auto_session
def delete(id: str, delete_message: bool = False, session: Optional[Session] = None) -> DeletionStatus:
    dbo = session.get(Thread, id)
    if dbo:
        # delete all messages that belong to this thread
        if delete_message:
            session.query(Message).where(Message.thread_id == id).delete()

        session.delete(dbo)
        session.commit()
    return DeletionStatus(id=id, object="thread.deleted", deleted=True)


@auto_session
def list(limit: int = 20, order: str = "desc", after: str = None, before: str = None, user_id: str = None, org_id: str = None, session: Optional[Session] = None) -> ThreadList:
    select_stmt = select(Thread)

    select_stmt = select_stmt.order_by(-Thread.created_at if order == "desc" else Thread.created_at)
    if after:
        select_stmt = select_stmt.filter(Thread.id > after)
    if before:
        select_stmt = select_stmt.filter(Thread.id < before)

    if user_id:
        select_stmt = select_stmt.filter(Thread.user_id == user_id)
    if org_id:
        select_stmt = select_stmt.filter(Thread.org_id == org_id)

    select_stmt = select_stmt.limit(limit)

    dbos = session.exec(select_stmt).all()
    rs = []
    for dbo in dbos:
        a = ThreadRead(**dbo.dict())
        a.metadata = dbo.metadata_
        rs.append(a)
    r = ThreadList(data=rs)
    return r
