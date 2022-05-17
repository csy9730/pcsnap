
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

test_is_chinese_weekday()
def main():
    guess_occasions()

if __name__ == "__main__":
    main()