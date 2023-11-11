import os
from typing import Optional, Dict, Any
import langchain.vectorstores as vectorstores


class Retrieval:
    def __init__(self) -> None:
        self._embeddings = None
        self._vectorstores = {}

    async def search(
        self,
        vs_name,
        query: str,
        k: int = 4,
        filter: Optional[Dict[str, Any]] = None,
        fetch_k: int = 20,
        **kwargs: Any
    ) -> Dict:
        vs = self._get_vectorstore(name=vs_name)
        docs = await vs.asimilarity_search_with_score(
            query=query,
            k=k,
            filter=filter,
            fetch_k=fetch_k,
            **kwargs
        )
        d = []
        for doc in docs:
            d.append({
                "doc": doc[0].dict(),
                "score": float(doc[1])
            })
        return d

    def _get_vectorstore_path(self, name):
        root = os.environ.get("VECTORSTORE_DIR")
        if not root:
            print("VECTORSTORE_DIR required")
            return None

        fname = os.path.join(root, name)
        return fname

    def _get_vectorstore(self, name):
        if name not in self._vectorstores:
            vs_path = self._get_vectorstore_path(name=name)
            vs = vectorstores.FAISS.load_local(vs_path, self.get_ebeddings(), normalize_L2=True)
            self._vectorstores[name] = vs
        return self._vectorstores[name]

    def get_ebeddings(self):
        if not self._embeddings:
            impl = os.environ.get("EMBEDDINGS_IMPL")
            model_name = os.environ.get("EMBEDDINGS_MODEL_NAME")
            device = os.environ.get("EMBEDDINGS_DEVICE")
            instruction = os.environ.get("EMBEDDINGS_INSTRUCTION")

            if impl == 'bge':
                from langchain.embeddings import HuggingFaceBgeEmbeddings
                from langchain.embeddings.huggingface import DEFAULT_QUERY_BGE_INSTRUCTION_ZH

                self._embeddings = HuggingFaceBgeEmbeddings(
                    model_name=model_name,
                    model_kwargs={'device': device if device else "cpu"},
                    query_instruction=instruction if instruction else DEFAULT_QUERY_BGE_INSTRUCTION_ZH
                )
        return self._embeddings


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv('.env')

    retrieval = Retrieval()

    result = retrieval.search(vs_name="uco", query="保湿")
    print(result)
