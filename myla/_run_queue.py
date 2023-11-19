import asyncio
from datetime import datetime
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

_run_tasks = asyncio.Queue()
_run_iters = dict()
_lock = asyncio.Lock()

def submit_run_task(run):
    _run_tasks.put_nowait(run)

async def get_run_task():
    return await _run_tasks.get()

async def create_run_iter(run_id):
    async with _lock:
        _run_iters[run_id] = AsyncIterator()
        logger.debug(f"Run iters: {_run_iters.keys()}")
        return _run_iters[run_id]

async def get_run_iter(run_id):
    async with _lock:
        logger.debug(f"Run iters: {_run_iters.keys()}")
        return _run_iters.get(run_id)

_last_clear_at = datetime.now().timestamp()
async def clear_iters():
    global _last_clear_at

    expires = 60*10
    now = datetime.now().timestamp()
    if _last_clear_at + expires > now:
        return
    async with _lock:
        expired = []
        for run_id, iter in _run_iters.items():
            if iter.created_at + expires < now:
                expired.append(run_id)

        for run_id in expired:
            _run_iters.pop(run_id)

        logger.info(f"Run iters cleared: {expired}")
    _last_clear_at = now
