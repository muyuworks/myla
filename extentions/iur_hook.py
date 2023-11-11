from typing import Optional, List, Dict
from muyu.hook import Hook

class IURHook(Hook):
    async def before(self, messages: List[Dict], metadata: Optional[Dict] = None):
        """
        :return: (LLM 上下文消息, 调用 LLM 的参数, 生成 Message 的 Metadata)
        """
        llm_message = [
            {
                "role": "system",
                "content": "你是欧舒丹天猫旗舰店的售前客服，正在与顾客对话。"
            }
        ]
        iur_query = None
        if messages and len(messages) > 0:
            iur_query = messages[-1]['content']
            messages[-1]['content'] = iur_query
        
        llm_message.extend(messages)
        metadata['iur_query'] = iur_query
        return llm_message, {"temperature": 0.5}, metadata