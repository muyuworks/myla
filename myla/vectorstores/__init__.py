import os
from ._base import Record, VectorStore
from ._embeddings import Embeddings
from .sentence_transformers_embeddings import SentenceTransformerEmbeddings
from .lancedb_vectorstore import LanceDB
from .faiss_vectorstore import FAISS


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