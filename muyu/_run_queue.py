import asyncio
from datetime import datetime

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
_run_iters = {}

async def submit_run_task(run):
    await _run_tasks.put(run)

async def get_run_task():
    return await _run_tasks.get()

def create_run_iter(run_id):
    _run_iters[run_id] = AsyncIterator()
    return _run_iters[run_id]

def get_run_iter(run_id):
    return _run_iters.get(run_id)

_last_clear_at = datetime.now().timestamp()
def clear_iters():
    now = datetime.now().timestamp()
    if _last_clear_at + 10*60 > now:
        return
    
    for run_id, iter in _run_iters.items():
        if iter.created_at + 10*60 < now:
            _run_iters.pop(run_id)