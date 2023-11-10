from typing import List, Dict
from muyu.hook import Hook

class IURHook(Hook):
    async def before(self, messages: List[Dict]):
        """
        :return: (LLM 上下文消息, 调用 LLM 的参数, 生成 Message 的 Metadata)
        """
        iur_query = None
        if messages and len(messages) > 0:
            iur_query = "中国的首都在哪"
            messages[-1]['content'] = iur_query
            messages.append({
                "role": "system",
                "content": "你的回答必须在结尾加上emoji符号"
            })
        return messages, {"temperature": 0.7}, {"IUR_Generated": iur_query}