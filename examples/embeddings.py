import asyncio
import numpy as np
import faiss
from myla.vectorstores.sentence_transformers_embeddings import SentenceTransformerEmbeddings

embeddings = SentenceTransformerEmbeddings(model_name="/Users/shellc/Downloads/bge-large-zh-v1.5")

v = asyncio.run(embeddings.aembed("hello"))

v = np.array([v], dtype=np.float32)

faiss.normalize_L2(v)

n = np.linalg.norm(v, ord=2)
print(n)
