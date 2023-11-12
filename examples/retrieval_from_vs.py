from muyu.retrieval import Retrieval

if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv('.env')

    retrieval = Retrieval()

    result = retrieval.search(vs_name="uco", query="保湿")
    print(result)