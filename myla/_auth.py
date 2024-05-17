from typing import Dict, Optional

from starlette.authentication import (AuthCredentials, AuthenticationBackend,
                                      SimpleUser)

from . import users


class AuthenticatedUser(SimpleUser):
    def __init__(self, id: str, username: str = None, orgs: Optional[Dict[str, users.OrganizationRead]] = None, primary_org_id: str = None) -> None:
        super().__init__(username)
        self.id = id
        self.orgs = orgs
        self.primary_org_id = primary_org_id

    @property
    def userid(self):
        return self.id


class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(self, request):
        secret_key = None
        if "Authorization" in request.headers:
            auth = request.headers["Authorization"]

            scheme, credentials = auth.split()
            if scheme.lower() == 'bearer':
                secret_key = credentials
        else:
            secret_key = request.cookies.get('secret_key')

        if secret_key:
            sk = users.get_secret_key(id=secret_key)
            if sk:
                orgs = users.list_orgs(user_id=sk.user_id).data

                org_map = {}
                primary_org_id = None
                for org in orgs:
                    org_map[org.id] = org
                    if org.user_id == sk.user_id:
                        primary_org_id = org.id

                auser = AuthenticatedUser(id=sk.user_id, orgs=org_map, primary_org_id=primary_org_id)

                scopes = ["authenticated"]
                credentials = AuthCredentials(scopes=scopes)

                return credentials, auser
