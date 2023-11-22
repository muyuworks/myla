import os
from ._base import Record, VectorStore
from ._embeddings import Embeddings
from .sentence_transformers_embeddings import SentenceTransformerEmbeddings
from .lancedb_vectorstore import LanceDB
from .faiss_vectorstore import FAISS
from . import pandas_loader

def get_default_embeddings():
    impl = os.environ.get("EMBEDDINGS_IMPL")
    model_name = os.environ.get("EMBEDDINGS_MODEL_NAME")
    device = os.environ.get("EMBEDDINGS_DEVICE")
    instruction = os.environ.get("EMBEDDINGS_INSTRUCTION")

    model_kwargs={'device': device if device else "cpu"}

    if not impl or impl == 'sentence_transformers':
        return SentenceTransformerEmbeddings(model_name=model_name, model_kwargs=model_kwargs, instruction=instruction)
    else:
        raise ValueError(f"Embedding implement not supported: {impl}")

_default_vs = {}

def get_default_vectorstore():
    impl = os.environ.get("VECTOR_STORE_IMPL")
    if not impl:
        raise ValueError("VECTOR_STORE_IMPL is required.")

    vs = _default_vs.get(impl)
    if not vs:
        vs_dir = os.environ.get("VECTORSTORE_DIR")
        if not vs_dir:
            raise ValueError("VECTORSTORE_DIR is required.")

        embeddings = get_default_embeddings()

        if impl == 'faiss':
            vs = FAISS(db_path=vs_dir, embeddings=embeddings)
        elif impl == 'lancedb':
            vs = LanceDB(db_uri=vs_dir, embeddings=embeddings)
        else:
            raise ValueError(f"VectorStore not suported: {impl}")
    
    return vs

def load_vectorstore_from_file(collection: str, fname: str, ftype: str):
    vs = get_default_vectorstore()

    if ftype in ['csv', 'xls', 'xlsx', 'json']:
        records = list(pandas_loader.PandasLoader(ftype=ftype).load(fname))
    else:
        raise ValueError("Invalid file type.")

    if len(records) == 0:
        return

    vs.create_collection(collection=collection, schema=records[0], mode='overwrite')

    vs.add(collection=collection, records=records)