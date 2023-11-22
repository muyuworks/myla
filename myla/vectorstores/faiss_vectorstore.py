import os
import json
from typing import List, Optional, Dict, Any
from ._base import Record, VectorStore
from ._embeddings import Embeddings
from .._logging import logger
from operator import itemgetter

def _import_langchain_vectorstores():
    try:
        import langchain.vectorstores as vectorstores
    except ImportError as exc:
        raise ImportError(
            "Could not import langchain.vectorstores python package. "
            "Please install it with `pip install langchain`."
        ) from exc
    return vectorstores

class FAISS(VectorStore):
    def __init__(self, db_path: str = None, embeddings: Embeddings = None) -> None:
        self._db_path = db_path
        self._embeddings = embeddings
        self._collections = {}

    def create_collection(self, collection: str, schema: Dict[str, type] = None, mode="create"):
        vectorstores = _import_langchain_vectorstores()
        vs = vectorstores.FAISS.from_texts(texts=[''], embedding=self.get_embeddings())
        vs.save_local(os.path.join(self._db_path, collection))
    
    def add(self, collection: str, records: List[Record], embeddings_columns: List[str] = None):
        vs = self._get_vectorstore(collection)

        text_to_embed = []
        for r in records:
            if embeddings_columns:
                v = itemgetter(*embeddings_columns, r)
            else:
                v = r
            text_to_embed.append(json.dumps(v, ensure_ascii=False))

        vs.add_texts(texts=text_to_embed, metadatas=records)
        vs.save_local(os.path.join(self._db_path, collection))
    
    def delete(self, collection: str, query: str):
        raise RuntimeError("Not implemented.")
    
    def search(self, collection: str = None, query: str = None, vector: List = None, filter: Any = None, limit: int = 20, columns: List[str] = None, with_vector: bool = False, with_distance: bool = False, **kwargs) -> List[Record]:
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
            vectorstores = _import_langchain_vectorstores()

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
