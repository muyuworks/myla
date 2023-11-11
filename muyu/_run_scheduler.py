import asyncio
from ._run_queue import get_run_task, create_run_iter, clear_iters
from ._llm import chat_complete

class RunScheduler:
    _instance = None

    def __init__(self) -> None:
        #self.tasks = set()
        pass

    @staticmethod
    def default():
        if not RunScheduler._instance:
            RunScheduler._instance = RunScheduler()
        return RunScheduler._instance

    async def start(self):
        async def consume():
            while True:
                run = await get_run_task()
                task = asyncio.create_task(
                    chat_complete(run=run, iter=await create_run_iter(run.id))
                )
                #self.tasks.add(task)

                await clear_iters()
        return asyncio.ensure_future(consume())