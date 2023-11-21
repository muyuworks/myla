from myla.tools import Tool, Context
from myla import llms

DOC_SUMMARY_INSTRUCTIONS_ZH = """
你是专业的文本分析助手, 你负责为用户问题生成候选答案。

你要使用下面的JSON格式的数据, query字段是提问, response字段是回答。

<数据开始>
{docs}
<数据结束>
用户提问: {query}

请为用户提问生成候选回答，如果用户提问不明确，请用户进一步说明， 生成结果不要包含问题。

候选回答:
"""
class QASummaryTool(Tool):
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

            messages = [] # 删除对话历史, 只保留 system Message 和最后一条用户消息
            for msg in context.messages:
                if not (msg['role'] == 'user' or msg['role'] == 'assistant'):
                    messages.append(msg)
            messages.append({"role": "user", "content": last_message})
            
            context.messages = messages