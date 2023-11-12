from .tools import Tool, Context
from . import llm, logger

INSTRUCTIONS_ZH = """
你是专业的文本分析助手, 下面是你和用户的对话:
-开始对话-
{history}
-结束对话-
最新用户问题: {last_user_message}
请你结合对话修改最新用户问题, 使修改后的用户问题包含完整意图。请直接输出修改后的结果。
修改后的用户问题:
"""

class IURTool(Tool):
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

        history = llm.plain_messages(messages=context.messages)

        iur_query = await llm.complete(INSTRUCTIONS_ZH.format(history=history, last_user_message=last_user_message), temperature=0)

        logger.info(f"Converstations: \n{history}\n IUR: {iur_query}")
        
        context.messages[-1]['content'] = iur_query

        context.message_metadata['iur'] = iur_query