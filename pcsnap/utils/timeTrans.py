import time


def toChromeTime(d):
    '''
    -- 13181125268490285 微秒
    -- select datetime('now')
    -- 2018-10-17 03:07:55
    -- select datetime('now','localtime')
    -- 2018-10-17 11:07:23

    -- 13181125268490285 微秒   Chrome时间戳
    -- 13181125268.490285 秒    Chrome时间戳
    -- 11644473600 间隔

    -- 13181125268490-11644473600  拿到的是Unix时间戳

    --  先转换为时间元组'''
    time_c = d/1000000-11644473600
    print(time_c)
    print(time.strftime("%Y-%m-%d %X", time.gmtime(time_c)))
    return time_c
    # 2018-09-11 07:41:08


if __name__ == "__main__":
    # toChromeTime(13181125268490285)
    toChromeTime(13249667223834478)  # 2020-11-12 15:07:03
    toChromeTime(13255239551294393)  # 2021-01-16 02:59:11

