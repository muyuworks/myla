from typing import Any, List, Optional, Dict
from ._base import Record, VectorStore
from ._embeddings import Embeddings


VECTOR_COLUMN_NAME = "vector"


class LanceDB(VectorStore):
    def __init__(self, db_uri, embeddings: Embeddings = None) -> None:
        super().__init__()

        try:
            import pyarrow as pa
        except ImportError as exc:
            raise ImportError(
                "Could not import pyarrow python package. "
                "Please install it with `pip install pyarrow`."
            ) from exc

        try:
            import lancedb as lancedb

            # disable diagnostics
            lancedb.utils.CONFIG['diagnostics'] = False
        except ImportError as exc:
            raise ImportError(
                "Could not import lancedb python package. "
                "Please install it with `pip install lancedb`."
            ) from exc

        self.db_uri = db_uri
        self.embeddings = embeddings

        self.db = lancedb.connect(self.db_uri)

        self.tables = {}

    def create_collection(self, collection: str, schema: Any = None, mode="create"):
        try:
            import pyarrow as pa
        except ImportError as exc:
            raise ImportError(
                "Could not import pyarrow python package. "
                "Please install it with `pip install pyarrow`."
            ) from exc
        if schema is None or not isinstance(schema, pa.Schema):
            raise ValueError("Invalid schema to create LanceDB table.")

        self.db.create_table(collection, schema=schema, mode=mode)

    def add(self, collection: str, records: List[Record]):
        tbl = self.db.open_table(collection)
        tbl.add(records)

    def delete(self, collection: str, query: str):
        tbl = self.db.open_table(collection)
        tbl.delete(query)

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
    ) -> List[Record]:
        if not query and not vector:
            raise ValueError("LanceDB search must provide query or vector.")

        if query and not vector and self.embeddings:
            vector = self.embeddings.embed(text=query)
        if not vector:
            raise ValueError(
                "LanceDB search must provide Embeddings function.")

        tbl = self.db.open_table(collection)

        query = tbl.search(vector)
        if filter:
            query = query.where(filter)

        if columns:
            query = query.select(columns=columns)

        results = query.limit(limit=limit).to_list()
        for v in results:
            if not with_vector:
                del v[VECTOR_COLUMN_NAME]
            if not with_distance:
                del v['_distance']

        return results
