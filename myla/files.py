from typing import List, Dict, Any, Optional, Union
from sqlmodel import Field, Session, Column, JSON, select
from pydantic import BaseModel
from ._models import auto_session, MetadataModel, DBModel, ReadModel, ListModel
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

def create(id: str, file: FileUpload, bytes:int, filename:str) -> FileRead:
    db_model = File(
        purpose=file.purpose,
        bytes=bytes,
        filename=filename,
        metadata_=file.metadata
    )

    dbo = create_model(id=id, object="file", meta_model=file, db_model=db_model)

    r = FileRead(**dbo.dict())
    r.metadata = dbo.metadata_

    return r

@auto_session
def list(purpose:str = None, limit: int = 20, order:str = "desc", after:str = None, before:str = None, session: Optional[Session] = None) -> FileList:
    select_stmt = select(File)

    if purpose:
        select_stmt = select_stmt.filter(File.purpose == purpose)

    select_stmt = select_stmt.order_by(-File.created_at if order == "desc" else File.created_at)
    if after:
        select_stmt = select_stmt.filter(File.id > after)
    if before:
        select_stmt = select_stmt.filter(File.id < before)

    select_stmt = select_stmt.limit(limit)
    
    dbos = session.exec(select_stmt).all()
    rs = []
    for dbo in dbos:
        a = FileRead(**dbo.dict())
        a.metadata = dbo.metadata_
        rs.append(a)
    r = FileList(data=rs)
    return r