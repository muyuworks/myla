import os
import threading
import pickle
import gc
import numpy as np
import pandas as pd
from typing import Any, Dict, List, Optional
from ._base import Record, VectorStore
from ._embeddings import Embeddings
from .. import utils


class FAISSGroupException(Exception):
    """"""


def _import_faiss():
    """Import faiss package."""
    try:
        import faiss
    except ImportError as exc:
        raise ImportError(
            "Could not import faiss python package. "
            "Please install it with `pip install faiss-cpu` or `pip install faiss-gpu`."
        ) from exc
    return faiss


class FAISSGroup(VectorStore):
    def __init__(self, path: str, embeddings: Embeddings = None) -> None:
        self._path = path
        self._embeddings = embeddings
        self._faiss = _import_faiss()

        os.makedirs(name=self._path, exist_ok=True)

        # lock the vs
        self._vs_lock = threading.Lock()
        self._col_locks = {}

        self._data = {}
        self._indexes = {}
        self._ids = {}

    def create_collection(self, collection: str, schema: Dict[str, type] = None, mode="create"):
        """Create a collection.

        :type mode:str
        :param mode: creation mode, create: raise FAISSGroupException if exists; overwrite: drop it if exists
        """
        col_path = os.path.join(self._path, collection)

        if mode == 'create' and os.path.exists(col_path):
            raise FAISSGroupException(f"Collection exists: {collection}")

        if mode == 'overwrite' and os.path.exists(col_path):
            self.drop(collection=collection)

        if not os.path.exists(col_path):
            os.mkdir(col_path)

    def add(
            self,
            collection: str,
            records: List[Record],
            embeddings_columns: Optional[List[str]] = None,
            vectors: Optional[List[List[float]]] = None,
            **kwargs
        ):
        """Add records to the collection."""
        group_by = kwargs.get('group_by')

        self._check_collection_exists(collection=collection)

        if records is None:
            raise ValueError(f"Invalid records: None")

        if not os.path.exists(os.path.join(self._path, collection)):
            raise FAISSGroupException(f"Collection not exists: {collection}")

        groups = self._group_records(records=records, group_by=group_by)

        if vectors:
            if len(vectors) != len(records):
                raise ValueError("The length of records must be the same as the length of vecotors.")
        else:
            text_to_embed = []
            for r in records:
                text_to_embed.append(Record.values_to_text(r, props=embeddings_columns))
            vectors = self._embeddings.embed_batch(texts=text_to_embed, instruction=kwargs.get('instruction'))

        with self._get_collection_lock(collection=collection):
            data, indexes, ids = self._load(collection=collection)

            idx_start = len(data)

            # add records to data
            for r in records:
                data.append(r)

            for gid, g_records_ids in groups.items():
                index = indexes.get(gid)
                id_map = ids.get(gid)

                if not index:
                    index = self._faiss.IndexFlatL2(len(vectors[0]))
                    id_map = []
                    indexes[gid] = index
                    ids[gid] = id_map

                g_vectors = []

                for i in g_records_ids:
                    g_vectors.append(vectors[i])
                    id = idx_start + i
                    id_map.append(id)

                g_vectors_npa = np.array(g_vectors, dtype=np.float32)
                self._faiss.normalize_L2(g_vectors_npa)
                index.add(g_vectors_npa)

            # save data
            self._save_data(collection=collection, data=data)
            gid_to_saved = groups.keys()
            for gid in gid_to_saved:
                self._save_group(collection=collection, gid=gid, index=indexes[gid], ids=ids[gid])

    def _group_id(self, v=None):
        if v is None or pd.isnull(v):
            v = ""
        if not isinstance(v, str):
            v = str(v)
        return utils.sha256(v.encode()).hex()

    def _group_records(self, records: List[Record], group_by: str):
        groups = {}

        if not group_by:
            groups[self._group_id("")] = range(len(records))
        else:
            for i in range(len(records)):
                gid = records[i].get(group_by)
                gid = self._group_id(gid)
                g = groups.get(gid)
                if not g:
                    g = []
                    groups[gid] = g
                g.append(i)
        return groups

    def _save_data(self, collection, data):
        fname = os.path.join(self._path, collection, "data.pkl")
        with open(fname, 'wb') as f:
            pickle.dump(data, f)

    def _save_group(self, collection, gid, index, ids):
        index_fname = os.path.join(self._path, collection, f"{gid}.index")
        self._faiss.write_index(index, index_fname)
        ids_fname = os.path.join(self._path, collection, f"{gid}.ids")
        with open(ids_fname, 'wb') as f:
            pickle.dump(ids, f)

    def delete(self, collection: str, query: str):
        return super().delete(collection, query)

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
        group_ids = kwargs.get('group_ids')

        self._check_collection_exists(collection=collection)

        if not query and not vector:
            raise FAISSGroupException("FAISSGroup search must provide query or vector.")

        if query and not vector and self._embeddings:
            vector = self._embeddings.embed(text=query, instruction=kwargs.get('instruction'))
        if not vector:
            raise FAISSGroupException("FAISSGroup search must provide Embeddings function.")

        vector = np.array([vector], dtype=np.float32)
        self._faiss.normalize_L2(vector)

        if group_ids is None:
            group_ids = [self._group_id()]
        else:
            group_ids = [self._group_id(v) for v in group_ids]

        if filter is not None:
            filter = {
                key: [value] if not isinstance(value, list) else value for key, value in filter.items()
            }

        data, indexes, ids = self._load(collection=collection)

        r_records = []
        for gid in group_ids:
            index = indexes.get(gid)
            id_map = ids.get(gid)
            if not index or not id_map:
                raise FAISSGroupException(f"group_id not exists: {gid}")

            distances, indices = index.search(vector, limit)
            for j, i in enumerate(indices[0]):
                if i == -1:
                    # This happens when not enough docs are returned.
                    continue
                _id = id_map[i]
                _distance = distances[0][j]
                record = data[_id]
                record['_distance'] = float(_distance)

                if filter:
                    if all(record.get(key) in value for key, value in filter.items()):
                        r_records.append(record)
                else:
                    r_records.append(record)

        distance_threshold = kwargs.get("distance_threshold")
        if distance_threshold is not None:
            r_records = [
                r for r in r_records if r['_distance'] < distance_threshold
            ]

        r_records.sort(key=lambda r: r['_distance'])

        return r_records[:limit]

    def drop(self, collection: str):
        """"""

    def _check_collection_exists(self, collection):
        if collection is None:
            raise ValueError(f"Invalid collection name: {collection}")
        if not os.path.exists(os.path.join(self._path, collection)):
            raise FAISSGroupException(f"Collection not exists: {collection}")

    def _load(self, collection: str):
        """Load collection data."""

        with self._vs_lock:
            data = self._data.get(collection)
            indexes = self._indexes.get(collection)
            ids = self._ids.get(collection)

            if not data:
                data = []
                indexes = {}
                ids = {}

                path = os.path.join(self._path, collection)
                for fname in os.listdir(path=path):
                    if fname == "data.pkl":
                        with open(os.path.join(path, fname), "rb") as f:
                            data = pickle.load(f)
                    if fname.endswith(".index"):
                        gid = fname.replace(".index", "")
                        idx = self._faiss.read_index(os.path.join(path, fname))
                        indexes[gid] = idx

                        id_map = []
                        with open(os.path.join(path, f"{gid}.ids"), "rb") as f:
                            id_map = pickle.load(f)
                        ids[gid] = id_map

                self._data[collection] = data
                self._indexes[collection] = indexes
                self._ids[collection] = ids

        return data, indexes, ids

    def _unload(self, collection: str):
        """Unload collection."""
        with self._vs_lock:
            if collection in self._data:
                del self._data[collection]
                del self._indexes[collection]
                del self._ids[collection]

                return gc.collect()

    def _get_collection_lock(self, collection):
        with self._vs_lock:
            lock = self._col_locks.get(collection)
            if not lock:
                lock = threading.Lock()
                self._col_locks[collection] = lock
            return lock
