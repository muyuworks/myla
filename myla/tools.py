from typing import Optional, List, Dict
from pydantic import BaseModel
import aiohttp
from ._logging import logger

class Context(BaseModel):
    # args, 有系统/LLM产生的调用 Tool 的参数，不可修改
    args: Dict = {}

    # 历史会话, 可修改, 最终会提交给 LLM
    messages: List[Dict] = []

    # Run 的 metadata, 不可修改
    run_metadata: Dict = {}

    # 设置调用 LLM 的参数, 可修改 
    llm_args: Dict = {}

    # 设置生成 Message 的 metadata
    message_metadata: Dict = {}

    # 可以使用的 Files
    file_ids: List[str] = []

    # 是否完成当前 Run, 如果是则会忽略后续所有 Tools 和 LLM 执行，直接将最后一条消息作为生成消息返回
    # 最后一条消息必须 role 为 assistant, 否则忽略
    is_completed: bool = False

    def get_last_message(self):
        """
        Get the last message

        return: None if messages is empty else the last messsage
        """
        if len(self.messages) == 0:
            return None
        else:
            return self.messages[-1]

class Tool:
    """
    Tool 被设置在 Assistant 或 Run 中, 会在 Run 执行过程中被调用。

    名称以 $ 开始的 tool 一定会被执行, 执行顺序为定义 Assistant/Run tools 的顺序
    名称不以 $ 开始的 tool 将由系统决定是否执行
    """
    async def execute(self, context: Context) -> None:
        pass

class HTTPTool(Tool):
    """
    以 HTTP API 调用远程 Tool 执行

    method: POST
    body: Context
    response body: Cotext
    """
    def __init__(self, url=None) -> None:
        super().__init__()
        self.url = url

    async def execute(self, context: Context) -> None:
        async with aiohttp.ClientSession() as session:
            async with session.post(url=self.url, json=context.messages) as resp:
                try:
                    if resp.status == 200:
                        result = await resp.json()
                        context.messages = result['messages']
                        context.llm_args.update(result['llm_args'])
                        context.message_metadata.update(result['message_metadata'])
                    else:
                        raise BaseException(f"status: {resp.status}")
                except Exception as e:
                    logger.warn(f"HTTP Tool execute failed: url={self.url} status={e}")
