from .tools import Tool, Context
from . import llms, logger
from .llms import utils

INSTRUCTIONS_ZH = """
你是专业的文本分析助手, 负责改写用户回复, 下面是AI助手和用户的对话记录, system 是AI助手的身份设定, user是用户, assistant是AI助手:
-开始对话-
{history}
-结束对话-
用户最新回复: {last_user_message}
请你结合对话记录改写用户最新回复。
如果用户最新回复是好的、谢谢、你好等问候语或礼貌性回复，不要改写用户回复。
如果用户最新回复是提问，请你以用户的身份改写，使其表述更清晰并包含用户的完整意图, 易于AI助手理解。

请直接输出修改后的结果，不要包含前缀说明。
改写后的用户回复:
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

        history = utils.plain_messages(messages=context.messages)

        iur_query = await llms.get().generate(INSTRUCTIONS_ZH.format(history=history, last_user_message=last_user_message), temperature=0)

        logger.debug(f"Converstations: \n{history}\n IUR: {iur_query}")
        
        context.messages[-1]['content'] = iur_query

        context.message_metadata['iur'] = iur_query