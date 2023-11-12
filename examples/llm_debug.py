import asyncio
import myla.llm as llm

async def main():
    r = await llm.chat_complete(messages=[{
        "role": "system",
        "content": "你是谁"
    }], stream=True)
    async for c in r:
        print(c)


if __name__ == '__main__':
    import dotenv
    dotenv.load_dotenv(".env")

    asyncio.run(main=main())