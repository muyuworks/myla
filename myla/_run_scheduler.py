import asyncio
from ._run_queue import get_run_task, create_run_iter, clear_iters
from ._llm import chat_complete
from ._logging import logger

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
                try:
                    run = await get_run_task()
                    logger.debug(f"RunScheduler received new task, run_id={run.id}")
                    iter = await create_run_iter(run.id)

                    task = asyncio.create_task(
                        chat_complete(run=run, iter=iter)
                    )
                    self.tasks.add(task)

                    await clear_iters()

                    done = []
                    for t in self.tasks:
                        if t.done():
                            done.append(t)
                    for t in done:
                        self.tasks.remove(t)
                        
                except Exception as e:
                    logger.error(f"RunScheduler error: {e}")  

        return asyncio.ensure_future(consume())