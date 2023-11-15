import asyncio
import myla.llms as llms

DOCS = """
[]
"""

QUERY = "送给谢顶男票的礼物"

INSTRUCTIONS = """
你是专业的问答分析助手。下面是JSON格式的问答记录。
<问答记录开始>
{docs}
<问答记录介绍>

请根据问答记录生成新问题的候选回答。
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