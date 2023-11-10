import asyncio
from .runs import RunRead
from ._run_queue import run_queue
from ._llm import chat_complete

class RunScheduler:
    _instance = None

    def __init__(self) -> None:
        self.tasks = set()

    @staticmethod
    def default():
        if not RunScheduler._instance:
            RunScheduler._instance = RunScheduler()
        return RunScheduler._instance

    async def start(self):
        async def consume():
            while True:
                run = await run_queue().get()
                task = asyncio.create_task(
                    chat_complete(run)
                )
                self.tasks.add(task)
        return asyncio.ensure_future(consume())