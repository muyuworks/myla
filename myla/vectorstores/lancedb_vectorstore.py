import json
from typing import Any, List, Optional, Dict
from operator import itemgetter
from ._base import Record, VectorStore
from ._embeddings import Embeddings

VECTOR_COLUMN_NAME = "_vector"


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

        self._db_uri = db_uri
        self._embeddings = embeddings

        self._db = lancedb.connect(self._db_uri)

        self._tables = {}

    def create_collection(self, collection: str, schema: Dict[str, type] = None, mode="create"):
        if schema is None:
            raise ValueError("Invalid schema to create LanceDB table.")

        s = self._convert_schema(schema=schema)

        self._db.create_table(collection, schema=s, mode=mode)

    def add(self, collection: str, records: List[Record], embeddings_columns: List[str] = None):
        tbl = self._db.open_table(collection)

        text_to_embed = []
        for r in records:
            if embeddings_columns:
                v = itemgetter(*embeddings_columns, r)
            else:
                v = r
            text_to_embed.append(json.dumps(v, ensure_ascii=False))

        embeds = self._embeddings.embed_batch(texts=text_to_embed)
        for i in range(len(records)):
            records[i][VECTOR_COLUMN_NAME] = embeds[i]

        tbl.add(records)

    def delete(self, collection: str, query: str):
        tbl = self._db.open_table(collection)
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

        if query and not vector and self._embeddings:
            vector = self._embeddings.embed(text=query)
        if not vector:
            raise ValueError(
                "LanceDB search must provide Embeddings function.")

        tbl = self._db.open_table(collection)

        query = tbl.search(vector, vector_column_name=VECTOR_COLUMN_NAME)
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

    def _convert_schema(self, schema: Dict[str, type]):
        try:
            import pyarrow as pa
        except ImportError as exc:
            raise ImportError(
                "Could not import pyarrow python package. "
                "Please install it with `pip install pyarrow`."
            ) from exc
        
        dims = len(self._embeddings.embed(""))
        columns = [
            pa.field(VECTOR_COLUMN_NAME, pa.list_(pa.float32(), dims)),
        ]

        for k, v in schema.items():
            t = pa.string()

            if isinstance(v, float):
                t = pa.float64()
            if isinstance(v, int):
                t = pa.int64
            if isinstance(v, bool):
                t = pa.bool_()

            columns.append(
                pa.field(k, t)
            )

        s = pa.schema(columns)

        return s
