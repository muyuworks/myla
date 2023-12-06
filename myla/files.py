from typing import List, Optional, Union
from sqlmodel import Field, Session, select
from . import _models


class FileUpload(_models.MetadataModel):
    purpose: str


class FileRead(_models.ReadModel):
    bytes: int
    filename: str
    purpose: str


class FileList(_models.ListModel):
    data: List[FileRead]


class File(_models.DBModel, table=True):
    bytes: int
    filename: Optional[str] = None
    purpose: str = Field(index=True)


@_models.auto_session
def create(id: str, file: FileUpload, bytes: int, filename: str, user_id: str = None, org_id: str = None, session: Optional[Session] = None) -> FileRead:
    db_model = File(
        purpose=file.purpose,
        bytes=bytes,
        filename=filename,
        metadata_=file.metadata
    )

    dbo = _models.create(id=id, object="file", meta_model=file, user_id=user_id, org_id=org_id, db_model=db_model, session=session)

    return dbo.to_read(FileRead)


@_models.auto_session
def get(id: str, user_id: str = None, session: Optional[Session] = None) -> Union[FileRead, None]:
    """Retrieval File object.

    Args:
        id(str): file id

    Returns:
        if file exists return FileRead object else return None
    """
    return _models.get(db_cls=File, read_cls=FileRead, id=id, user_id=user_id, session=session)


@_models.auto_session
def delete(id: str, user_id: str = None, session: Optional[Session] = None) -> _models.DeletionStatus:
    return _models.delete(db_cls=File, id=id, user_id=user_id, session=session)


@_models.auto_session
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
        rs.append(dbo.to_read(FileRead))
    r = FileList(data=rs)
    return r
