import json
from myla.vectorstores import get_default_vectorstore
from myla.tools import Tool, Context
from myla._logging import logger
import logging


class QARetrievalTool(Tool):
    def __init__(self) -> None:
        super().__init__()
        self._vs = get_default_vectorstore()

    async def execute(self, context: Context) -> None:
        if len(context.messages) == 0:
            logger.debug("History is empty, skip retrieval")
            return

        collections = context.file_ids if context.file_ids else []

        if len(collections) == 0:
            logger.debug(
                "no retrieval collections specified, skip retrieval")
            return

        args = {"limit": 20, "with_distance": True}
        if "retrieval_limit" in context.run_metadata:
            args["limit"] = context.run_metadata["retrieval_limit"]

        #queries = []
        #for m in context.messages[-3:]:
        #    if m.get('role') == 'user':
        #        queries.append(m["content"])
        #query = '\n'.join(queries)
        query = context.messages[-1]['content']

        records = []
        for c in collections:
            r_records = await self._vs.asearch(collection=c, query=query, **args)
            for r in r_records:
                records.append(r)
        records.sort(key=lambda r: r['_distance'], reverse=True)

        if records and len(records) > 0:
            messages = context.messages[:-1]
            last_message = context.messages[-1]

            for r in records:
                r_messages = r.get('messages')
                if r_messages is not None and isinstance(r_messages, list):
                    for m in r_messages:
                        role = m.get('role')
                        content = m.get('content')
                        if role is not None and content is not None:
                            messages.append({
                                'role': role,
                                'content': content,
                                'distance': r['_distance']
                            })

            messages.append(last_message)
            context.messages = messages
        if logger.level == logging.DEBUG:
            logger.debug(f"Retrieval messages: {json.dumps(context.messages, ensure_ascii=False, indent=1)}")
