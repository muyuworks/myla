import asyncio
from myla.retrieval import Retrieval

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv('.env')

    retrieval = Retrieval()

    coro = retrieval.search(vs_name="default", query="保湿")
    result = asyncio.run(coro)
    print(result)