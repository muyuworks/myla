from myla.tools import Tool, Context
from myla import llms, logger
from myla.llms import utils

INSTRUCTIONS = """
Given an ongoing conversation and a follow up question, your task is to rephrase the follow-up question. \
While rephrasing take into account the context of ongoing conversation to form a standalone question \
that delivers more information than the follow up question. If the follow up question is not related to the \
ongoing conversation, simply rephrase the question.

Chat History:
{history}

Follow Up Question: {last_user_message}
Standalone Question:
"""


class Rephrase(Tool):
    async def execute(self, context: Context) -> None:
        """
        根据会话历史让 LLM 决定是否需要改写用户最后一条消息
        """
        last_user_message = None
        if len(context.messages) > 0:
            if context.messages[-1]["role"] == "user":
                last_user_message = context.messages[-1]['content']

        if not last_user_message:
            return

        history = utils.plain_messages(messages=context.messages, roles=["user", "assistant"])

        question = await llms.get().generate(INSTRUCTIONS.format(history=history, last_user_message=last_user_message), temperature=0)
        question = question.strip()

        logger.debug(f"History: {history}\nRephrased Question: {question}")

        context.messages[-1]['content'] = question

        context.message_metadata['rephrase'] = question
