from myla.vectorstores.lancedb_vectorstore import LanceDB
import pyarrow as pa
from myla.vectorstores.sentence_transformers_embeddings import SentenceTransformerEmbeddings

embeddings = SentenceTransformerEmbeddings(model_name="/Users/shellc/Downloads/bge-large-zh-v1.5")

vs = LanceDB(db_uri="/tmp/lancedb", embeddings=embeddings)

collection = "default"

schema = pa.schema(
    [
        pa.field("vector", pa.list_(pa.float32(), 1024)),
        pa.field("text", pa.string())
    ]
)
vs.create_collection(collection=collection, schema=schema, mode='overwrite')

embds = embeddings.embed("hello")

vs.add(collection=collection, records=[{"vector": embds, "text": "hello"}])

print(vs.search(collection=collection, query="hello", columns=['text']))

vs.delete(collection=collection, query="text = 'hello'")