import os
import json
from ._base import Record, VectorStore
from ._embeddings import Embeddings
from .sentence_transformers_embeddings import SentenceTransformerEmbeddings
from .lancedb_vectorstore import LanceDB
from .faiss_vectorstore import FAISS
from . import pandas_loader, pdf_loader
from .._logging import logger
from ..utils import create_instance

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

_loaders = {}

def load_loaders():
    """Load configured Loaders."""
    loaders_cfg = os.environ.get("LOADERS")
    if not loaders_cfg:
        return

    loaders = json.loads(loaders_cfg)
    for c in loaders:
        try:
            name = c.get("name")
            impl = c.get("impl")
            if not name or not impl:
                logger.warn(f"Invalid Loader config: name={name}, impl={impl}")
                continue
            instance = create_instance(impl)
            _loaders[name] = instance
        except Exception as e:
            logger.warn(f"Create Loader failed: {e}", exc_info=e)

def get_loader_instance(name: str):
    """Get configured Loader."""
    return _loaders.get(name)

def load_vectorstore_from_file(collection: str, fname: str, ftype: str, embeddings_columns = None, loader: str = None):
    vs = get_default_vectorstore()

    if loader:
        loader_ = get_loader_instance(loader)
    elif ftype in ['csv', 'xls', 'xlsx', 'json']:
        loader_ = pandas_loader.PandasLoader(ftype=ftype)
    elif ftype == 'pdf':
        loader_ = pdf_loader.PDFLoader()
    else:
        raise ValueError("Invalid file type.")

    records = list(loader_.load(file=fname))

    if len(records) == 0:
        return

    vs.create_collection(collection=collection, schema=records[0], mode='overwrite')

    vs.add(collection=collection, records=records, embeddings_columns=embeddings_columns)