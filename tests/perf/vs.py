import os
from datetime import datetime
import pickle
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

from myla import utils
from myla.vectorstores import get_default_embeddings, get_default_vectorstore, pandas_loader

here = os.path.abspath(os.path.dirname(__file__))

os.environ['EMBEDDINGS_IMPL'] = 'sentence_transformers'
os.environ['EMBEDDINGS_MODEL_NAME'] = '/Users/shellc/Downloads/bge-large-zh-v1.5'
os.environ['EMBEDDINGS_DEVICE'] = 'mps'

os.environ['VECTORSTORE_DIR'] = os.path.join(here, 'vs')
os.environ['VECTOR_STORE_IMPL'] = 'faissg'

data_input = os.path.join(here, 'bq1.csv')
embeds_output = os.path.join(here, 'embeds.pkl')

embeddings = get_default_embeddings()
vs = get_default_vectorstore()


def load_records():
    return list(pandas_loader.PandasLoader().load(data_input))


def records_stat():
    df = pd.read_csv(data_input)
    df['len'] = df.apply(lambda x : len(x['sentence1']) + len(x['sentence2']), axis=1)
    df['len1'] = df['sentence1'].apply(lambda x : len(x))
    s = pd.concat([df['len'].describe(), df['len1'].describe()], axis=1)
    print(s)


def embed():
    embedings = get_default_embeddings()
    records = load_records()

    texts = [r['sentence1'] for r in records]

    embeds = embedings.embed_batch(texts=texts)
    with open(embeds_output, 'wb') as f:
        pickle.dump(embeds, f)


def test_embed():
    embed()


def create_col(records=None, vectors=None):
    if not records:
        records = load_records()
    if not vectors:
        vectors = pickle.load(open(embeds_output, 'rb'))

    print(f"length: record={len(records)}, vectors={len(vectors)}")

    col_name = utils.random_id()
    vs.create_collection(collection=col_name, schema=records[0])

    return col_name


def test_add_batch(records=None, vectors=None):
    records = load_records()
    vectors = pickle.load(open(embeds_output, 'rb'))

    col_name = create_col(records=records, vectors=vectors)

    begin = datetime.now().timestamp()
    vs.add(collection=col_name, records=records, vectors=vectors)
    end = datetime.now().timestamp()

    print(os.environ['VECTOR_STORE_IMPL'], "elapsed", end-begin)


def test_add():
    records = load_records()
    vectors = pickle.load(open(embeds_output, 'rb'))

    col_name = create_col(records=records, vectors=vectors)

    vs.add(collection=col_name, records=records, vectors=vectors)

    begin = datetime.now().timestamp()
    for i in range(1000): #range(len(records)):
        vs.add(collection=col_name, records=[records[i]], vectors=[vectors[i]])
    end = datetime.now().timestamp()

    print(os.environ['VECTOR_STORE_IMPL'], "elapsed", end-begin)


def test_search():
    records = load_records()
    vectors = pickle.load(open(embeds_output, 'rb'))

    col_name = create_col(records=records, vectors=vectors)

    vs.add(collection=col_name, records=records, vectors=vectors, group_by='label')

    begin = datetime.now().timestamp()
    for i in range(1000):
        vs.search(collection=col_name, vector=vectors[i], group_ids=[0])
    end = datetime.now().timestamp()

    print(os.environ['VECTOR_STORE_IMPL'], "elapsed", end-begin)


def test_search_multi_trehads():
    records = load_records()
    vectors = pickle.load(open(embeds_output, 'rb'))

    col_name = create_col(records=records, vectors=vectors)

    vs.add(collection=col_name, records=records, vectors=vectors)

    def _search(i):
        vs.search(collection=col_name, vector=vectors[i])

    executor = ThreadPoolExecutor(max_workers=10)
    futures = []

    begin = datetime.now().timestamp()
    for i in range(1000):
        futures.append(executor.submit(_search, i=i))

    for f in futures:
        f.done()
        f.result()

    end = datetime.now().timestamp()

    print(os.environ['VECTOR_STORE_IMPL'], "elapsed", end-begin)


def test_multi_vs():
    records = load_records()
    vectors = pickle.load(open(embeds_output, 'rb'))

    cols = []
    for i in range(100):
        rs = records[:100].copy()
        col_name = create_col(records=rs, vectors=vectors)
        vs.add(collection=col_name, records=rs, vectors=vectors[:100])
        cols.append(col_name)

    import time
    time.sleep(100)


if __name__ == '__main__':
    #records = load_records()
    #vectors = pickle.load(open(embeds_output, 'rb'))

    #records_stat()

    #test_embed()

    #test_add_batch()
    #test_add()

    #test_search()
    #test_search_multi_trehads()

    #test_multi_vs()

    import time
    time.sleep(100000)
