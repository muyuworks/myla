import os
from typing import List, Optional, Dict, Any
from ._base import Record, VectorStore
from ._embeddings import Embeddings
from .._logging import logger

class FAISS(VectorStore):
    def __init__(self, db_path: str = None, embeddings: Embeddings = None) -> None:
        self._db_path = db_path
        self._embeddings = embeddings
        self._collections = {}

    def create_collection(self, collection: str, schema: Any = None, mode="create"):
        return super().create_collection(collection, schema = schema, mode=mode)
    
    def add(self, collection: str, records: List[Record]):
        return super().add(collection, records)
    
    def delete(self, collection: str, query: str):
        return super().delete(collection, query)
    
    def search(self, collection: str = None, query: str = None, vector: List = None, filter: Any = None, limit: int = 20, columns: List[str] | None = None, with_vector: bool = False, with_distance: bool = False, **kwargs) -> List[Record] | None:
        return self._faiss_search(collection_name=collection, query=query, k=limit, fetch_k=limit*10)

    def _faiss_search(
        self,
        collection_name,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
        fetch_k: int = 20,
        **kwargs: Any
    ) -> Dict:
        vs = self._get_vectorstore(name=collection_name)
        docs = vs.similarity_search_with_score(
            query=query,
            k=k,
            filter=filter,
            fetch_k=fetch_k,
            **kwargs
        )

        d = []
        for doc in docs:
            v = doc[0].dict()
            v['_distance'] = float(doc[1])
            d.append(v)
        return d

    def _get_vectorstore_path(self, name):
        if not self._db_path:
            logger.warn("db_path required")
            return None

        fname = os.path.join(self._db_path, name)
        return fname

    def _get_vectorstore(self, name):
        if name not in self._collections:
            try:
                import langchain.vectorstores as vectorstores
            except ImportError as exc:
                raise ImportError(
                    "Could not import langchain.vectorstores python package. "
                    "Please install it with `pip install langchain`."
                ) from exc

            vs_path = self._get_vectorstore_path(name=name)
            vs = vectorstores.FAISS.load_local(
                vs_path, self.get_embeddings(), normalize_L2=True)
            self._collections[name] = vs
        return self._collections[name]

    def get_embeddings(self):
        if not self._embeddings:
            raise ValueError("No default embeddings found.")
        
        from langchain.schema.embeddings import Embeddings as Embeddings_
        class LCEmbeddings(Embeddings_):
            def __init__(self, embed) -> None:
                self.embed = embed

            def embed_documents(self, texts: List[str]) -> List[List[float]]:
                return self.embed.embed_batch(texts)
            def embed_query(self, text: str) -> List[float]:
                return self.embed.embed(text)

        return LCEmbeddings(embed=self._embeddings)
