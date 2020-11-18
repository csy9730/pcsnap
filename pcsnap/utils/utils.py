import time


def timeCount(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        ret = func(*args, **kwargs)
        end = time.perf_counter()
        print(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()), end-start)
        return ret
    return wrapper


def aTimeCount(func):
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        ret = await func(*args, **kwargs)
        end = time.perf_counter()
        print(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()), end-start)
        return ret
    return wrapper