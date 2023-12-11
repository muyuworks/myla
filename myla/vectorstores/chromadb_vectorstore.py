import math
from typing import Any, List, Optional, Dict
from ._base import Record, VectorStore
from ._embeddings import Embeddings
from .. import utils


class Chromadb(VectorStore):
    def __init__(self, path, embeddings: Embeddings = None) -> None:
        super().__init__()

        try:
            import chromadb
        except ImportError as exc:
            raise ImportError(
                "Could not import chromadb python package. "
                "Please install it with `pip install chromadb`."
            ) from exc
        self._embeddings = embeddings
        self._db = chromadb.PersistentClient(path=path)

    def create_collection(self, collection: str, schema: Dict[str, type] = None, mode="create"):
        """Create a new collection"""
        self._db.create_collection(name=collection)

    def add(self, collection: str, records: List[Record], embeddings_columns: List[str] = None, vectors: List[List[float]] = None):
        """Add record to the vectorsotre"""
        col = self._db.get_collection(name=collection)

        ids = []
        text_to_embed = []
        for r in records:
            ids.append(utils.random_id())
            text_to_embed.append(Record.values_to_text(r, props=embeddings_columns))

        if not vectors:
            vectors = self._embeddings.embed_batch(texts=text_to_embed)

        if len(vectors) != len(records):
            raise ValueError("The length of records must be the same as the length of vecotors.")

        batch_size = 40000
        batchs = math.ceil(len(records) / batch_size)
        for i in range(batchs):
            b = i*batch_size
            e = (i+1)*batch_size
            if len(ids[b:e]) == 0:
                break
            col.add(ids=ids[b:e], embeddings=vectors[b:e], documents=text_to_embed[b:e], metadatas=records[b:e])

    def delete(self, collection: str, query: str):
        """Delete record from the vectorstore"""

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
        col = self._db.get_collection(name=collection)

        include = ['metadatas', 'documents']
        if with_vector:
            include.append('embeddings')
        if with_distance:
            include.append('distances')

        res = col.query(
            query_embeddings=[vector] if vector else None,
            query_texts=[query] if query else None,
            n_results=limit,
            include=include
        )

        result = []
        i = 0
        for r in res['metadatas']:
            record = r[0]
            if with_vector:
                record['vecotor'] = res['embeddings'][i][0]
            if with_distance:
                record['_distantce'] = res['distances'][i][0]
            result.append(record)

            i += 1
        return result
