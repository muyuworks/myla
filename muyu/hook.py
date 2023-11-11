from typing import Optional, List, Dict
import aiohttp


class Hook:
    async def before(self, messages: List[Dict], metadata: Optional[Dict] = None):
        """
        :return: (LLM 上下文消息, 调用 LLM 的参数, 生成 Message 的 Metadata)
        """
        return messages, None, metadata

    async def after(self):
        ...


class HTTPHook(Hook):
    def __init__(self, url=None) -> None:
        super().__init__()
        self.url = url

    async def before(self, messages: List[Dict], metadata: Optional[Dict] = None):
        async with aiohttp.ClientSession() as session:
            async with session.post(url=self.url, json=messages) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result["messages"], result["args"], result["metadata"]
                else:
                    # raise BaseException(f"HTTPHook failed: {resp.status}")
                    print(f"HTTPHook failed: {resp.status}")
                    return messages, None, metadata
