from starlette.authentication import (
    AuthCredentials, AuthenticationBackend, SimpleUser
)
from . import users


class AuthenticatedUser(SimpleUser):
    def __init__(self, id: str, username: str = None) -> None:
        super().__init__(username)
        self.id = id

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
                auser = AuthenticatedUser(id=sk.user_id)

                scopes = ["authenticated"]
                credentials = AuthCredentials(scopes=scopes)

                return credentials, auser
