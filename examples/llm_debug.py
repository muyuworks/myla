import asyncio
from myla.llms.openai import OpenAI
from myla.llms.chatglm import ChatGLM

async def main():
    openai = ChatGLM()
    r = await openai.chat(messages=[{
            "role": "system",
            "content": "你是谁"
        }],
        stream=True,
        model="/Users/shellc/Workspaces/chatglm.cpp/chatglm-ggml.bin"
    )
    print(r)
    async for c in r:
        print(c)


if __name__ == '__main__':
    import dotenv
    dotenv.load_dotenv(".env")

    asyncio.run(main=main())