import asyncio
import myla.llms as llms

DOCS = """
[]
"""

QUERY = "送给谢顶男票的礼物"

INSTRUCTIONS = """
你是专业的电商客服对话分析助手, 你需要根据要求对客服对话进行分析。

客服对话是JSON格式的数据, query是客户提问, response是客服回答。

下面是需要分析的客服对话:
<客服对话开始>
{docs}
<客服对话结束>

请根据客服对话生成新问题的候选回答。
新问题: {query}
候选回答:
"""

async def main():
    r = await llms.get().chat(messages=[{
        "role": "system",
        "content": INSTRUCTIONS.format(docs=DOCS, query=QUERY)
    }], stream=False)
    print(r)


if __name__ == '__main__':
    import dotenv
    dotenv.load_dotenv(".env")

    asyncio.run(main=main())