import json
from .vectorstores import get_default_vectorstore
from .tools import Tool, Context
from ._logging import logger
from . import llms

RETRIEVAL_INSTRUCTIONS_EN = """
Refer to the retrievals to generate your answer.
"""

RETRIEVAL_INSTRUCTIONS_ZH = """
参考 Retrievals 信息生成你的回答。
"""


class RetrievalTool(Tool):
    def __init__(self) -> None:
        super().__init__()
        self._vs = get_default_vectorstore()

    async def execute(self, context: Context) -> None:
        if len(context.messages) == 0:
            logger.debug("History is empty, skip retrieval")
            return

        collections = context.file_ids if context.file_ids else []

        if 'retrieval_collection' in context.run_metadata:
            collections.append(context.run_metadata["retrieval_collection"])

        if len(collections) == 0:
            logger.debug(
                "no retrieval collections specified, skip retrieval")
            return

        args = {"limit": 20, "with_distance": True}
        if "retrieval_limit" in context.run_metadata:
            args["limit"] = context.run_metadata["retrieval_limit"]
        distance = 1
        if "retrieval_distance" in context.run_metadata:
            distance = context.run_metadata['retrieval_distance']

        query = context.messages[-1]["content"]

        docs = []
        for c in collections:
            r_docs = await self._vs.asearch(collection=c, query=query, **args)
            for doc in r_docs:
                if doc['_distance'] < distance:
                    docs.append(doc)

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
                "content": "<Retrievals Begin>"
            })
            messages.append({
                "role": "system",
                "content": json.dumps(docs, ensure_ascii=False),
                "type": "docs"
            })
            messages.append({
                "role": "system",
                "content": "<Retrievals End>"
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
