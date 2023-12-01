import uuid as _uuid
import hashlib
import base64 as base64_
import time
import asyncio
import importlib

namespace = _uuid.uuid1()


def uuid():
    return _uuid.uuid5(namespace, _uuid.uuid1().hex)


def sha1(s: bytes):
    m = hashlib.sha1()
    m.update(s)
    return m.digest()


def sha256(s: bytes):
    m = hashlib.sha256()
    m.update(s)
    return m.digest()


def sha384(s: bytes):
    m = hashlib.sha384()
    m.update(s)
    return m.digest()


def base32(s: bytes):
    return base64_.b32encode(s=s)


def base64(s: bytes):
    return base64_.b64encode(s, altchars=b'PS')


def random_id():
    return base32(sha1(uuid().bytes)).decode().lower()


def random_key():
    return base64(sha384(uuid().bytes)).decode()


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
    except RuntimeError:
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


def create_instance(module_name: str, *args, **kwargs):
    try:
        ss = module_name.split('.')
        module = importlib.import_module('.'.join(ss[:-1]))
        instance = getattr(module, ss[-1])(*args, **kwargs)
        return instance
    except Exception as e:
        raise ImportError(f"Create instance failed, module: {module_name}") from e
