from typing import Optional, List, Union
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Session, select
from . import _models
from . import utils


class UserOrgLink(SQLModel, table=True):
    org_id: str = Field(foreign_key="organization.id", primary_key=True)
    user_id: str = Field(foreign_key="user.id", primary_key=True)


class OrganizationBase(BaseModel):
    """Represents the basic information of an organization."""
    display_name: Optional[str]


class OrganizationCreate(_models.MetadataModel, OrganizationBase):
    """Represents the Organization to be created."""


class OrganizationRead(_models.ReadModel, OrganizationBase):
    """Represents the Organization read."""
    is_primary: bool


class OrganizationList(_models.ListModel):
    """Represents the Organization list."""
    data: List[OrganizationRead] = []


class Organization(_models.DBModel, OrganizationBase, table=True):
    """Represents the user saved in db."""
    is_primary: bool = Field(index=True, default=False)
    #users: List["User"] = Relationship(back_populates="orgs", link_model=UserOrgLink)


class UserBase(BaseModel):
    """Represents the basic information of a user."""
    username: str = Field(index=True, unique=True)
    display_name: Optional[str]


class UserCreate(_models.MetadataModel, UserBase):
    """Represents the user to be created."""
    password: str


class UserRead(_models.ReadModel, UserBase):
    """Represents the user read."""
    is_sa: Optional[bool]
    orgs: List[Organization] = []


class UserList(_models.ListModel):
    """Represents the user list."""
    data: List[UserRead] = []


class User(_models.DBModel, UserBase, table=True):
    """Represents the user saved in db."""
    is_sa: Optional[bool] = Field(default=False)
    salt: str
    password: str
    #orgs: List[Organization] = Relationship(back_populates="users", link_model=UserOrgLink)


class SecretKeyBase(BaseModel):
    display_name: Optional[str]
    tag: Optional[str] = Field(index=True)


class SecrectKeyCreate(_models.MetadataModel, SecretKeyBase):
    """Secrect object to be created."""


class SecretKeyRead(_models.ReadModel, SecretKeyBase):
    """The SecrectKey read."""
    user_id: str


class SecrectKeyList(_models.ListModel):
    data: List[SecretKeyRead] = []


class SecretKey(_models.DBModel, SecretKeyBase, table=True):
    """"""


class UserLogin(BaseModel):
    username: str
    password: str


class UserLoginResult(BaseModel):
    user: UserRead
    secret_key: SecretKeyRead


def create_organization(org: OrganizationCreate, is_primary: bool = False, user_id: str = None, session: Optional[Session] = None, auto_commit=True) -> OrganizationRead:
    db_model = Organization.from_orm(org)
    db_model.is_primary = is_primary
    db_model.user_id = user_id

    dbo = _models.create(object="organization", meta_model=org, db_model=db_model, session=session, auto_commit=auto_commit)
    r = OrganizationRead(**dbo.dict())
    r.metadata = dbo.metadata_
    return r


@_models.auto_session
def get_organization(id: str, session: Optional[Session] = None):
    r = None
    dbo = session.get(Organization, id)
    if dbo:
        r = OrganizationRead(**dbo.dict())
        r.metadata = dbo.metadata_

    return r


def generate_password(password: str, salt: str):
    s = f"{password} {salt}"
    return utils.base64(utils.sha384(s=s.encode())).decode()


@_models.auto_session
def create_user(user: UserCreate, is_sa: bool = False, session: Session = None) -> UserRead:
    salt = utils.random_key()
    password = generate_password(user.password, salt)

    db_model = User(salt=salt, is_sa=is_sa, **user.dict())
    db_model.password = password

    if not user.display_name:
        db_model.display_name = user.username

    user_created = _models.create(object="user", meta_model=user, db_model=db_model, session=session, auto_commit=False)

    org = OrganizationCreate(display_name=user.username)
    org_created = create_organization(org=org, is_primary=True, user_id=user_created.id, session=session, auto_commit=False)

    link = UserOrgLink(org_id=org_created.id, user_id=user_created.id)
    session.add(link)

    r = UserRead(**user_created.dict())
    r.metadata = user_created.metadata_

    session.commit()
    return r


@_models.auto_session
def get_user_dbo(id: str, session: Session = None):
    return session.get(User, id)


@_models.auto_session
def get_user(id: str, session: Session = None):
    r = None
    dbo = get_user_dbo(id=id, session=session)
    if dbo:
        r = UserRead(**dbo.dict())
        r.metadata = dbo.metadata_

    return r


@_models.auto_session
def get_user_by_uername(username: str, session: Session) -> Union[UserRead, None]:
    stmt = select(User).where(User.username == username)

    from sqlalchemy.exc import NoResultFound
    try:
        dbo = session.exec(statement=stmt).one() # raise exception if none
        return dbo
    except NoResultFound:
        return None


@_models.auto_session
def delete_user(id: str, session: Session = None) -> _models.DeletionStatus:
    dbo = get_user_dbo(id=id, session=session)
    session.delete(dbo)
    session.commit()
    return _models.DeletionStatus(id=id, object="user", deleted=True)


@_models.auto_session
def list_orgs(user_id: str, session: Session = None):
    stmt = select(Organization, UserOrgLink).where(Organization.id == UserOrgLink.org_id).filter(UserOrgLink.user_id == user_id)
    dbos = session.exec(statement=stmt).all()

    rs = []
    for dbo in dbos:
        a = OrganizationRead(**dbo[0].dict())
        rs.append(a)
    r = OrganizationList(data=rs)
    return r


@_models.auto_session
def list_users(sa_only: bool = False, session: Session = None) -> UserList:
    stmt = select(User)
    if sa_only:
        stmt = stmt.where(User.is_sa == True)
    dbos = session.exec(statement=stmt).all()

    rs = []
    for dbo in dbos:
        a = UserRead(**dbo.dict())
        rs.append(a)
    r = UserList(data=rs)
    return r


@_models.auto_session
def list_sa_users(session: Session = None) -> UserList:
    return list_users(sa_only=True, session=session)


@_models.auto_session
def create_secret_key(key: SecrectKeyCreate, user_id: str, session: Session = None) -> SecretKeyRead:
    db_model = SecretKey.from_orm(key)

    secret_key = utils.random_key()

    dbo = _models.create(object="secret_key", meta_model=key, db_model=db_model, id=secret_key, user_id=user_id, session=session)

    r = SecretKeyRead(**dbo.dict())
    r.metadata = dbo.metadata_

    return r


@_models.auto_session
def get_secret_key(id: str, session: Session = None) -> SecretKeyRead:
    r = None
    dbo = session.get(SecretKey, id)
    if dbo:
        r = SecretKeyRead(**dbo.dict())
        r.metadata = dbo.metadata_

    return r


@_models.auto_session
def list_secret_keys(user_id: str, session: Session = None):
    stmt = select(SecretKey).filter(SecretKey.user_id == user_id).order_by(-SecretKey.created_at)
    dbos = session.exec(statement=stmt).all()

    rs = []
    for dbo in dbos:
        a = SecretKeyRead(**dbo.dict())
        rs.append(a)
    r = SecrectKeyList(data=rs)
    return r


@_models.auto_session
def delete_secret_key(id: str, user_id: str, session: Session = None) -> _models.DeletionStatus:
    stmt = select(SecretKey).filter(SecretKey.user_id == user_id)
    dbos = session.exec(statement=stmt).all()

    to_delete = []
    for sk in dbos:
        if sk.id[-4:] == id[-4:]:
            to_delete.append(sk)
    if len(to_delete) > 1:
        raise ValueError("Conflict")
    else:
        session.delete(to_delete[0])
        session.commit()

    return _models.DeletionStatus(id=id, object="secret_key", deleted=True)


@_models.auto_session
def create_default_superadmin(session: Session = None):
    """Create the default super admin user."""
    sa = list_sa_users(session=session)
    if len(sa.data) == 0:
        return create_user(user=UserCreate(username='admin', password='admin'), is_sa=True, session=session)


@_models.auto_session
def login(user: UserLogin, session: Session = None) -> Union[UserLoginResult, None]:
    stmt = select(User).where(User.username == user.username)

    from sqlalchemy.exc import NoResultFound
    try:
        dbo = session.exec(statement=stmt).one() # raise exception if none
    except NoResultFound:
        return None

    pwd_g = generate_password(password=user.password, salt=dbo.salt)
    if pwd_g == dbo.password:
        r = UserRead(**dbo.dict())
        r.metadata = dbo.metadata_

        sks = list_secret_keys(user_id=r.id, session=session)
        sk_web = None
        for sk in sks.data:
            if sk.tag == 'web':
                sk_web = sk

        if not sk_web:
            sk_web = create_secret_key(key=SecrectKeyCreate(tag='web'), user_id=r.id, session=session)

        return UserLoginResult(user=r, secret_key=sk_web)
    else:
        return None


@_models.auto_session
def change_password(user_id: str, new_password: str, session: Session = None) -> Union[UserRead, None]:
    dbo = session.get(User, user_id)
    if dbo:
        pwd = generate_password(new_password, dbo.salt)
        dbo.password = pwd
        session.add(dbo)
        session.commit()
        session.refresh(dbo)
        r = UserRead(**dbo.dict())
        r.metadata = dbo.metadata_
        return r
