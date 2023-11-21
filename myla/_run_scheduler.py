from datetime import datetime
import asyncio
from ._llm import chat_complete
from ._logging import logger

class AsyncIterator:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.created_at = datetime.now().timestamp()

    def __aiter__(self):
        return self

    async def __anext__(self):
        i = await self.queue.get()
        if i is None:
            raise StopAsyncIteration

        return i

    async def put(self, item):
        await self.queue.put(item)

class RunScheduler:
    _instance = None

    def __init__(self) -> None:
        self._tasks = set()
        self._run_queue = asyncio.Queue()
        self._run_iters = dict()
        self._run_iters_lock = asyncio.Lock()
        self._last_clear_at = datetime.now().timestamp()

    @staticmethod
    def default():
        if not RunScheduler._instance:
            RunScheduler._instance = RunScheduler()
        return RunScheduler._instance

    def submit_run(self, run):
        self._run_queue.put_nowait(run)

    async def _create_run_iter(self, run_id):
        async with self._run_iters_lock:
            self._run_iters[run_id] = AsyncIterator()
            logger.debug(f"Run iters: {self._run_iters.keys()}")
            return self._run_iters[run_id]

    async def get_run_iter(self, run_id):
        async with self._run_iters_lock:
            logger.debug(f"Run iters: {self._run_iters.keys()}")
            return self._run_iters.get(run_id)

    async def _clear_iters(self):
        expires = 60*10
        now = datetime.now().timestamp()
        if self._last_clear_at + expires > now:
            return
        async with self._run_iters_lock:
            expired = []
            for run_id, iter in self._run_iters.items():
                if iter.created_at + expires < now:
                    expired.append(run_id)

            for run_id in expired:
                self._run_iters.pop(run_id)

            logger.info(f"Run iters cleared: {expired}")
        self.last_clear_at = now

    def start(self):
        async def _start():
            while True:
                try:
                    run = await self._run_queue.get()
                    logger.debug(f"RunScheduler received new task, run_id={run.id}")
                    iter = await self._create_run_iter(run.id)

                    task = asyncio.create_task(
                        chat_complete(run=run, iter=iter)
                    )
                    self._tasks.add(task)

                    await self._clear_iters()

                    done = []
                    for t in self._tasks:
                        if t.done():
                            done.append(t)
                    for t in done:
                        self._tasks.remove(t)
                except Exception as e:
                    logger.error(f"RunScheduler error: {e}")
        return asyncio.create_task(_start())