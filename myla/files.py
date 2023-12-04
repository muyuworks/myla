from typing import List, Optional, Union
from sqlmodel import Field, Session, select
from ._models import auto_session, MetadataModel, DBModel, ReadModel, ListModel, DeletionStatus
from ._models import create as create_model


class FileUpload(MetadataModel):
    purpose: str


class FileRead(ReadModel):
    bytes: int
    filename: str
    purpose: str


class FileList(ListModel):
    data: List[FileRead]


class File(DBModel, table=True):
    bytes: int
    filename: Optional[str] = None
    purpose: str = Field(index=True)


@auto_session
def create(id: str, file: FileUpload, bytes: int, filename: str, user_id: str = None, org_id: str = None, session: Optional[Session] = None) -> FileRead:
    db_model = File(
        purpose=file.purpose,
        bytes=bytes,
        filename=filename,
        metadata_=file.metadata
    )

    dbo = create_model(id=id, object="file", meta_model=file, user_id=user_id, org_id=org_id, db_model=db_model, session=session)

    r = FileRead(**dbo.dict())
    r.metadata = dbo.metadata_

    return r


@auto_session
def get(id: str, session: Optional[Session] = None) -> Union[FileRead, None]:
    """Retrieval File object.

    Args:
        id(str): file id

    Returns:
        if file exists return FileRead object else return None
    """
    r = None
    dbo = session.get(File, id)
    if dbo:
        d = dbo.dict()
        r = FileRead(**d)
        r.metadata = dbo.metadata_
    return r


@auto_session
def delete(id: str, session: Optional[Session] = None) -> DeletionStatus:
    dbo = session.get(File, id)
    if dbo:
        session.delete(dbo)
        session.commit()
    return DeletionStatus(id=id, object="file.deleted", deleted=True)


@auto_session
def list(purpose: str = None, limit: int = 20, order: str = "desc", after: str = None, before: str = None, user_id: str = None, org_id: str = None, session: Optional[Session] = None) -> FileList:
    select_stmt = select(File)

    if purpose:
        select_stmt = select_stmt.filter(File.purpose == purpose)

    select_stmt = select_stmt.order_by(-File.created_at if order == "desc" else File.created_at)
    if after:
        select_stmt = select_stmt.filter(File.id > after)
    if before:
        select_stmt = select_stmt.filter(File.id < before)

    if user_id:
        select_stmt = select_stmt.filter(File.user_id == user_id)
    if org_id:
        select_stmt = select_stmt.filter(File.org_id == org_id)

    select_stmt = select_stmt.limit(limit)

    dbos = session.exec(select_stmt).all()
    rs = []
    for dbo in dbos:
        a = FileRead(**dbo.dict())
        a.metadata = dbo.metadata_
        rs.append(a)
    r = FileList(data=rs)
    return r
