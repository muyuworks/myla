from myla.vectorstores.lancedb_vectorstore import LanceDB
from myla.vectorstores.sentence_transformers_embeddings import SentenceTransformerEmbeddings
from myla.vectorstores.pandas_loader import PandasLoader

embeddings = SentenceTransformerEmbeddings(model_name="/Users/shellc/Downloads/bge-large-zh-v1.5")

vs = LanceDB(db_uri="/tmp/lancedb", embeddings=embeddings)

collection = "default"

records = list(PandasLoader().load("./data/202101.csv"))

vs.create_collection(collection=collection, schema=records[0], mode='overwrite')

vs.add(collection=collection, records=records)

print(vs.search(collection=collection, query="新疆"))

#vs.delete(collection=collection, query="text = 'hello'")
