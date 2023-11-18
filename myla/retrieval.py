import os
import json
from typing import Optional, Dict, Any
from .vectorstores import get_default_embeddings, LanceDB, FAISS
from .tools import Tool, Context
from ._logging import logger
from . import llms

RETRIEVAL_INSTRUCTIONS_EN = """
You should refer to the content below to generate your response. 
The reference content is an array in JSON format, where each record represents a reference content record. 
The `doc` attribute of a reference content record represents the reference content, 
while the `score` attribute represents the relevance score between the reference content and the question.
The higher the score, the higher the relevance. 

The reference content is enclosed in the <DOCS> tag.
"""

RETRIEVAL_INSTRUCTIONS_ZH = """
优先参考<DOCS>标签中的内容对最新的问题进行回答。
"""


class RetrievalTool(Tool):
    def __init__(self, vector_store_impl=None) -> None:
        super().__init__()
        self._embeddings = get_default_embeddings()
        self._vecotr_store_impl = vector_store_impl

        if not self._vecotr_store_impl:
            self._vecotr_store_impl = os.environ.get("VECTOR_STORE_IMPL")

        if not self._vecotr_store_impl:
            raise ValueError("VECTOR_STORE_IMPL is required.")

        self._vector_store_dir = os.environ.get("VECTORSTORE_DIR")
        if not self._vector_store_dir:
            raise ValueError("VECTORSTORE_DIR is required.")

        if self._vecotr_store_impl == 'faiss':
            self._vs = FAISS(db_path=self._vector_store_dir, embeddings=self._embeddings)
        elif self._vecotr_store_impl == 'lancedb':
            self._vs = LanceDB(db_uri=self._vector_store_dir, embeddings=self._embeddings)
        else:
            raise ValueError(f"VectorStore not suported: {self._vecotr_store_impl}")

    async def execute(self, context: Context) -> None:
        if len(context.messages) == 0:
            logger.debug("History is empty, skip retrieval")
            return

        if "retrieval_collection" not in context.run_metadata:
            logger.debug(
                "no retrieval_collection in run_metadata, skip retrieval")
            return

        collection = context.run_metadata["retrieval_collection"]
        args = {}
        if "retrieval_limit" in context.run_metadata:
            args["limit"] = context.run_metadata["retrieval_limit"]

        query = context.messages[-1]["content"]

        docs = await self._vs.asearch(collection=collection, query=query)
        #logger.debug("Retrieval docs:" + json.dumps(docs, ensure_ascii=False))
        if docs and len(docs) > 0:
            messages = context.messages
            last_message = messages[-1]
            messages = messages[:-1]

            messages.append({
                "role": "system",
                "content": RETRIEVAL_INSTRUCTIONS_ZH,
            })
            messages.append({
                "role": "system",
                "content": "<DOCS>"
            })
            messages.append({
                "role": "system",
                "content": json.dumps(docs, ensure_ascii=False),
                "type": "docs"
            })
            messages.append({
                "role": "system",
                "content": "</DOCS>"
            })
            messages.append(last_message)
            context.messages = messages


DOC_SUMMARY_INSTRUCTIONS_ZH = """
你是专业的问答分析助手。下面是JSON格式的问答记录。
<问答记录开始>
{docs}
<问答记录介绍>

请根据问答记录生成新问题的候选回答。
新问题: {query}
候选回答:
"""


class DocSummaryTool(Tool):
    async def execute(self, context: Context) -> None:
        if len(context.messages) == 0:
            return

        last_message = context.messages[-1]['content']

        docs = None

        for msg in context.messages:
            if msg.get('type') == 'docs':
                docs = msg

        if docs:
            summary = await llms.get().chat(messages=[{
                "role": "system",
                "content": DOC_SUMMARY_INSTRUCTIONS_ZH.format(docs=docs['content'], query=last_message)
            }], stream=False, temperature=0)
            if summary:
                docs['content'] = summary
