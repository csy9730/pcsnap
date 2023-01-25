import time
from typing import Callable, Awaitable

def timeCount(func:Callable):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        ret = func(*args, **kwargs)
        end = time.perf_counter()
        print(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()), end-start)
        return ret
    return wrapper


def aTimeCount(func:Awaitable):
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        ret = await func(*args, **kwargs)
        end = time.perf_counter()
        print(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()), end-start)
        return ret
    return wrapper