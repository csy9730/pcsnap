
from calendar import month
import datetime
import time



def guess_occasions(x=None):
    if x is None:
        x = datetime.datetime.now()
    # print(x.date(),type(x.date()),x.date().timetuple())

    is_weekday = is_chinese_weekday(x)
    if is_weekday:
        if x.time() < datetime.time(7,30,0):
            return ["sleeping"]
        if x.time() < datetime.time(9,0,0):
            return ["life"]
        elif x.time()>=datetime.time(9,0,0) and x.time()<=datetime.time(18,0,0):
            return ["work"]
        elif x.time()<=datetime.time(23,30,0):
            return "after work"
        else:
            return ["sleeping"]
    else:
        if x.time() < datetime.time(8,0,0):
            return ["sleeping"]
        if x.time() < datetime.time(9,0,0):
            return ["life"]
        elif x.time()>=datetime.time(9,0,0) and x.time()<=datetime.time(18,0,0):
            return ["study", "misc"]
        elif x.time()<=datetime.time(23,59,0):
            return ["study", "misc", "relax"]
        else:
            return ["sleeping"]

def datetime_demo():
    x = datetime.date(2022,5,2)
    print(x)
    print(x.isoweekday(), x.weekday())
    # 星期一到星期天，对应 isoweekday[1~7]  weekday[0~6]
def datetime2_demo():
    x = datetime.datetime.now()
    print(x.time()<datetime.time(12,34,56))

def time_demo():
    print(time.localtime())


def is_chinese_weekday(x):
    special_days = {(2022, 1,3),(2022, 1,29),(2022, 1,30),(2022, 1,31),(2022, 2,1),(2022, 2,2),(2022, 2,3),(2022, 2,4),
        (2022, 4,2),(2022, 4,4),(2022, 4,5),(2022, 4,24),(2022, 5,2),(2022, 5,3),(2022, 5,4),(2022, 5,7),(2022, 6,3),(2022, 9,120),
        (2022, 10,3),(2022, 10,4),(2022, 10,5),(2022, 10,6),(2022, 10,7),(2022, 10,8),(2022, 10,9),
    }
    
    if isinstance(x, datetime.date):
        x = (x.year, x.month, x.day)
    if x in special_days:
        x = datetime.date(*x)
        if x.isoweekday()<= 5:
            return False
        else:
            return True
    else:
        x = datetime.date(*x)
        if x.isoweekday()<= 5:
            return True
        else:
            return False
    
def test_is_chinese_weekday():
    assert not is_chinese_weekday((2022,1,3))
    assert is_chinese_weekday((2022,5,7))
    assert not is_chinese_weekday((2022,5,8))
    assert is_chinese_weekday((2022,5,9))
    assert not is_chinese_weekday(datetime.date(2022,5,15))
    assert is_chinese_weekday(datetime.date(2022,5,17))

def get_deltatime(dt):
    # a='3d12m56c'
    import re
    ss = re.split('([Mwdhm])', dt) # ['3', 'd', '12', 'm', '56c']
    tt = [0, 0, 0, 0, 0] # M,w,d,h,m
    for s in ss:
        if s.isdigit():
            d = int(s)
        else:
            if s == 'M':
                tt[0] = d
            elif s == 'w':
                tt[1] = d
            elif s == 'd':
                tt[2] = d
            elif s == 'h':
                tt[3] = d
            elif s == 'm':
                tt[4] = d
            # else:
            #     print(s, d)
    return datetime.timedelta(days=tt[0]*30+tt[1]*7+tt[2],hours=tt[3],minutes=tt[4])

def test_deltatime():
    print(get_deltatime('1d2h30m'))

def datetimestr_2_dt(s=None):
    if s is None:
        return datetime.datetime.now()

    if "-" in s or "_" in s:
        dt = datetime.datetime.now() - get_deltatime(s[1:])
        return dt
    elif "+" in s:
        return datetime.datetime.now() + get_deltatime(s[1:])
        
    if len(s) == 4 and s.isdigit():
        return datetime.datetime(year=datetime.date.today().year, month=int(s[:2]), day=int(s[2:]), hour=12)
    elif len(s) == 8 and s.isdigit():
        return datetime.datetime(year=int(s[:4]), month=int(s[4:6]), day=int(s[6:]), hour=12)
    elif len(s) == 6 and s.isdigit():
        return datetime.datetime.combine(datetime.date.today(), datetime.time(hour=int(s[:2]), minute=int(s[2:4]), second=int(s[4:])))

def test_datetimestr_2_dt():
    print(datetimestr_2_dt())
    dt = datetimestr_2_dt("1101")
    print(dt)
    dt = datetimestr_2_dt("20221101")
    print(dt)
    dt = datetimestr_2_dt("123456")
    print(dt)

    dt = datetimestr_2_dt("-1d6h")
    print(dt)
    dt = datetimestr_2_dt("+1d1h10m")
    print(dt)

def main():
    # guess_occasions()
    # test_is_chinese_weekday()
    test_datetimestr_2_dt()
    test_deltatime()

if __name__ == "__main__":
    main()