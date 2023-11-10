import asyncio

_queue = asyncio.Queue()

def run_queue():
    return _queue