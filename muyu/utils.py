import uuid as _uuid
import hashlib
import time

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