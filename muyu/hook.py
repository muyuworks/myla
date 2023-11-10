import json
from typing import List, Dict
import asyncio
import aiohttp


class Hook:
    async def before(self, messages: List[Dict]):
        """
        :return: (LLM 上下文消息, 调用 LLM 的参数, 生成 Message 的 Metadata)
        """
        return messages, None, None

    async def after(self):
        ...


class HTTPHook(Hook):
    def __init__(self, url=None) -> None:
        super().__init__()
        self.url = url

    async def before(self, messages: List[Dict]):
        async with aiohttp.ClientSession() as session:
            print(json.dumps(messages))
            async with session.post(url=self.url, json=messages) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result["messages"], result["args"], result["metadata"]
                else:
                    # raise BaseException(f"HTTPHook failed: {resp.status}")
                    print(f"HTTPHook failed: {resp.status}")
                    return messages, None, None
