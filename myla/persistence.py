from typing import Optional, Dict, Any
import os
import json

from sqlmodel import SQLModel, create_engine, Session
from ._logging import logger

class Persistence:
    _instance = None

    def __init__(self, database_url: Optional[str] = None, connect_args: Optional[Dict[str, Any]] = None) -> None:
        self._database_url = database_url
        self._connect_args = connect_args

        if not database_url and 'DATABASE_URL' in os.environ:
            self._database_url = os.environ['DATABASE_URL']
        if not connect_args and 'DATABASE_CONNECT_ARGS' in os.environ:
            self._connect_args = json.loads(
                os.environ['DATABASE_CONNECT_ARGS'])
        if not self._database_url:
            #raise ValueError("database_url is required.")
            logger.warn("DATABASE_URL not specified, use sqlite:///myla.db")
            self._database_url = 'sqlite:///myla.db'
        if not self._connect_args:
            self._connect_args = {}
        
        self._engine = create_engine(
            self._database_url,
            connect_args=self._connect_args,
            json_serializer=lambda obj: json.dumps(obj, ensure_ascii=False)
        )

    @property
    def engine(self):
        return self._engine
    
    def create_session(self) -> Session:
        return Session(self._engine)
    
    def initialize_database(self):
        SQLModel.metadata.create_all(self._engine)

    @staticmethod
    def default():
        if not Persistence._instance:
            Persistence._instance = Persistence()
        return Persistence._instance
    