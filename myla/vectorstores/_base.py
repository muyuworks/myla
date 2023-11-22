from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
from functools import partial
import asyncio


class Record(Dict):
    pass


class VectorStore(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def create_collection(self, collection: str, schema: Dict[str, type] = None, mode="create"):
        """Create a new collection"""

    @abstractmethod
    def add(self, collection: str, records: List[Record], embeddings_columns: List[str] = None):
        """Add record to the vectorsotre"""

    @abstractmethod
    def delete(self, collection: str, query: str):
        """Delete record from the vectorstore"""

    @abstractmethod
    def search(
        self,
        collection: str = None,
        query: str = None,
        vector: List = None,
        filter: Any = None,
        limit: int = 20,
        columns: Optional[List[str]] = None,
        with_vector: bool = False,
        with_distance: bool = False,
        **kwargs
    ) -> Optional[List[Record]]:
        """Search records"""

    async def asearch(
        self,
        collection: str = None,
        query: str = None,
        vector: List = None,
        filter: Any = None,
        limit: int = 20,
        columns: Optional[List[str]] = None,
        with_vector: bool = False,
        with_distance: bool = False,
        **kwargs
    ):
        return await asyncio.get_running_loop().run_in_executor(
            None, partial(self.search, **kwargs), collection, query, vector, filter, limit, columns, with_vector, with_distance
        )