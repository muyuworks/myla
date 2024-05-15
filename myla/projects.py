from typing import Optional

from . import _models


class Project(_models.DBModel, table=True):
    name: Optional[str] = None
