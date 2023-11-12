import os
import json
from typing import Optional, Dict, Any
import langchain.vectorstores as vectorstores
from .tools import Tool, Context
from ._logging import logger

RETRIEVAL_INSTRUCTIONS_EN="""
You should refer to the content below to generate your response. 
The reference content is an array in JSON format, where each record represents a reference content record. 
The `doc` attribute of a reference content record represents the reference content, 
while the `score` attribute represents the relevance score between the reference content and the question.
The higher the score, the higher the relevance. 

The reference content is enclosed in the <DOCS> tag.
"""

class RetrievalTool(Tool):
    def __init__(self) -> None:
        super().__init__()

        self.retrieval = Retrieval()

    async def execute(self, context: Context) -> None:
        if len(context.messages) == 0:
            logger.debug("History is empty, skip retrieval")
            return

        if "retrieval_collection_name" not in context.run_metadata:
            logger.debug(
                "not retrieval_collection_name in run_metadata, skip retrieval")
            return

        vs_name = context.run_metadata["retrieval_collection_name"]
        args = {}
        if "retrieval_top_k" in context.run_metadata:
            args["top_k"] = context.run_metadata["retrieval_top_k"]

        query = context.messages[-1]["content"]

        docs = await self.retrieval.search(vs_name=vs_name, query=query, **args)
        context.messages.append({
            "role": "system",
            "content": RETRIEVAL_INSTRUCTIONS_EN,
        })
        context.messages.append({
            "role": "system",
            "content": "<DOCS>",
        })
        context.messages.append({
            "role": "system",
            "content": json.dumps(docs, ensure_ascii=False),
            "type": "docs"
        })
        context.messages.append({
            "role": "system",
            "content": "<DOCS>",
        })


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
            logger.warn("VECTORSTORE_DIR required")
            return None

        fname = os.path.join(root, name)
        return fname

    def _get_vectorstore(self, name):
        if name not in self._vectorstores:
            vs_path = self._get_vectorstore_path(name=name)
            vs = vectorstores.FAISS.load_local(
                vs_path, self.get_ebeddings(), normalize_L2=True)
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
