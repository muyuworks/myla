import json
import os
from typing import Optional

from .._logging import logger
from ..utils import create_instance
from . import pandas_loader, pdf_loader
from ._base import Record, VectorStore
from ._embeddings import Embeddings
from .chromadb_vectorstore import Chromadb
from .faiss_group import FAISSGroup
from .faiss_vectorstore import FAISS
from .lancedb_vectorstore import LanceDB

_default_embeddings = None


def get_default_embeddings():
    global _default_embeddings

    if _default_embeddings is None:
        impl = os.environ.get("EMBEDDINGS_IMPL")
        model_name = os.environ.get("EMBEDDINGS_MODEL_NAME")
        device = os.environ.get("EMBEDDINGS_DEVICE")
        instruction = os.environ.get("EMBEDDINGS_INSTRUCTION")
        multi_process = os.environ.get("EMBEDDINGS_MULTI_PROCESS")
        multi_process_devices = os.environ.get("EMBEDDINGS_MULTI_PROCESS_DEVICES")

        if multi_process is not None and multi_process.lower() == "true":
            multi_process = True
        else:
            multi_process = False

        if multi_process_devices is not None:
            multi_process_devices = multi_process_devices.split(",")
        model_kwargs = {'device': device if device else "cpu"}

        if not impl or impl == 'sentence_transformers':
            from .sentence_transformers_embeddings import \
                SentenceTransformerEmbeddings
            _default_embeddings = SentenceTransformerEmbeddings(
                model_name=model_name,
                model_kwargs=model_kwargs,
                instruction=instruction,
                multi_process=multi_process,
                multi_process_devices=multi_process_devices
            )
        elif impl == 'xinference':
            from .xinference_embeddings import XinferenceEmbeddings

            base_url = os.environ.get("XINFERENCE_BASE_URL")
            model_id = os.environ.get("XINFERENCE_MODEL_ID")

            _default_embeddings = XinferenceEmbeddings(
                base_url=base_url,
                model_id=model_id,
                instruction=instruction
            )
        else:
            raise ValueError(f"Embedding implement not supported: {impl}")
    return _default_embeddings


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
        elif impl == 'chromadb':
            vs = Chromadb(path=vs_dir, embeddings=embeddings)
        elif impl == 'faissg':
            vs = FAISSGroup(path=vs_dir, embeddings=embeddings)
        else:
            raise ValueError(f"VectorStore not suported: {impl}")
        _default_vs[impl] = vs
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


def load_vectorstore_from_file(collection: str, fname: str, ftype: str, embeddings_columns=None, loader: Optional[str] = None, **kwargs):
    vs = get_default_vectorstore()

    if loader:
        loader_ = get_loader_instance(loader)
    elif ftype in ['csv', 'xls', 'xlsx', 'json']:
        loader_ = pandas_loader.PandasLoader(ftype=ftype)
    elif ftype == 'pdf':
        loader_ = pdf_loader.PDFLoader()
    else:
        raise ValueError("Invalid file type.")

    if not loader_:
        raise RuntimeError(f"Loader not found: {loader}")

    records = list(loader_.load(file=fname, metadata=kwargs.get("metadata")))

    if len(records) == 0:
        return

    vs.create_collection(collection=collection, schema=records[0], mode='overwrite')

    vs.add(
        collection=collection,
        records=records,
        embeddings_columns=embeddings_columns,
        group_by=kwargs.get('group_by'),
        instruction=kwargs.get('instruction')
    )
