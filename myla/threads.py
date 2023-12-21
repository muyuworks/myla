from datetime import datetime
from typing import Optional, Union, List
from sqlmodel import Session
from . import _models
from .messages import Message


class ThreadEdit(_models.MetadataModel):
    # message list
    pass


class ThreadCreate(ThreadEdit):
    pass


class ThreadModify(ThreadEdit):
    pass


class ThreadRead(_models.ReadModel):
    pass


class ThreadList(_models.ListModel):
    data: List[ThreadRead] = []


class Thread(_models.DBModel, table=True):
    """
    Represents an assistant that can call the model and use tools.
    """


@_models.auto_session
def create(thread: ThreadCreate, user_id: str = None, org_id: str = None, session: Session = None) -> ThreadRead:
    db_model = Thread.from_orm(thread)
    dbo = _models.create(object="thread", meta_model=thread, db_model=db_model, user_id=user_id, org_id=org_id, session=session)
    return dbo.to_read(ThreadRead)


@_models.auto_session
def get(id: str, user_id: str = None, session: Session = None) -> Union[ThreadRead, None]:
    return _models.get(db_cls=Thread, read_cls=ThreadRead, id=id, user_id=user_id, session=session)


@_models.auto_session
def modify(id: str, thread: ThreadEdit, user_id: str = None, session: Session = None):
    return _models.modify(db_cls=Thread, read_cls=ThreadRead, id=id, to_update=thread.dict(exclude_unset=True), user_id=user_id, session=session)


@_models.auto_session
def delete(id: str, user_id: str = None, mode="soft", session: Optional[Session] = None) -> _models.DeletionStatus:
    dbo = session.get(Thread, id)
    if dbo and (not user_id or user_id == dbo.user_id):
        deleted_at = int(datetime.now().timestamp()*1000)
        if mode is not None and mode == 'soft':
            dbo.is_deleted = True
            dbo.deleted_at = deleted_at
            session.add(dbo)

            session.query(Message).where(Message.thread_id == id).update({Message.is_deleted: True, Message.deleted_at: deleted_at})

            session.commit()
            session.refresh(dbo)
        else:
            session.delete(dbo)
            session.query(Message).where(Message.thread_id == id).delete()
            session.commit()
    return _models.DeletionStatus(id=id, object="thread.deleted", deleted=True)


@_models.auto_session
def list(
        limit: int = 20,
        order: str = "desc",
        after: str = None,
        before: str = None,
        user_id: str = None,
        org_id: str = None,
        session: Optional[Session] = None
    ) -> ThreadList:
    return _models.list(
        db_cls=Thread,
        read_cls=ThreadRead,
        list_cls=ThreadList,
        limit=limit,
        order=order,
        after=after,
        before=before,
        user_id=user_id,
        org_id=org_id,
        session=session
    )
