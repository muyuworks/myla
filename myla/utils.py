import uuid as _uuid
import hashlib
import time
import asyncio

namespace = _uuid.uuid1()


def uuid():
    return _uuid.uuid5(namespace, _uuid.uuid1().hex).hex


def sha1(s: str):
    m = hashlib.sha1()
    m.update(s.encode())
    return m.hexdigest()


def sha256(s: str):
    m = hashlib.sha256()
    m.update(s.encode())
    return m.hexdigest()

def retry(func, rety_times=3):
    def inner(*args, **kwargs):
        for i in range(rety_times):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                print(f"Retry {func}, times={i}, e={e}")
                time.sleep(3)
                continue
    return inner


def ensure_event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError as e:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop=loop)
    return loop

def sync_call(async_func, *args, **kwargs):
    loop = ensure_event_loop()

    task = loop.create_task(async_func(*args, **kwargs))
    loop.run_until_complete(task)
    return task.result()

def sync_iter(async_iter, *args, **kwargs):
    loop = ensure_event_loop()

    aiter = async_iter(*args, **kwargs).__aiter__()
    async def get_next():
        try:
            v = await aiter.__anext__()
            return False, v
        except StopAsyncIteration:
            return True, None
    while True:
        done, v = loop.run_until_complete(get_next())
        if done:
            break
        yield v