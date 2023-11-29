import asyncio
from myla.vectorstores.sentence_transformers_embeddings import SentenceTransformerEmbeddings

embeddings = SentenceTransformerEmbeddings(model_name="/Users/shellc/Downloads/bge-large-zh-v1.5")

print(asyncio.run(embeddings.aembed("hello")))
