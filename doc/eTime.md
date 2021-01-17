# time

    

## GMT
GMT：即格林尼治标准时间

## UTC

UTC是协调时间，含义为：一切以我为基准，全部想我看齐。所以称它为世界标准时间是没毛病的，而把GMT称作格林威治当地时间更为合适（也叫旧的标准时间）。

JS获取当前时间戳，可以通过Date.now()方法来实现，返回自1970年1月1日00:00:00 UTC以来经过的毫秒数也就是当前时间戳。

时间戳是指格林威治时间1970年01月01日00时00分00秒(北京时间1970年01月01日08时00分00秒)起至现在的总毫秒数。


    
``` js
var aDate = new Date(1324966722383.4478);  // Tue Dec 27 2011 14:18:42 GMT+0800 (中国标准时间)
aDate.toLocaleString();     // "2011/12/27 下午2:18:42"


 var time = Date.now(); // 1610788609010
 var d = new Date(time); // Sat Jan 16 2021 17:16:49 GMT+0800 (中国标准时间) {}

```

``` python
import time 
f = time.time()     # 1610789154.6302474

time.gmtime(f)  
# time.struct_time(tm_year=2021, tm_mon=1, tm_mday=16, tm_hour=9, tm_min=26, tm_sec=36, tm_wday=5, tm_yday=16, tm_isdst=0)

time.localtime(time.time())  
# 转换成新的时间格式
dt = time.strftime("%Y-%m-%d %H:%M:%S",time_local)
print(dt)
```


对于HTTP来说，GMT完全等于UTC(协调世界时)。

### chrome timestamp


 chrome 浏览器的时间戳是从 1601-01-01 0:0:0 开始纪元的呢


 ``` python
def toChromeTime(d):
    ''' 先转换为时间元组'''
    time_c = d/1000000-11644473600
    print(time_c)
    print(time.strftime("%Y-%m-%d %X", time.gmtime(time_c)))
    return time_c
    # 2018-09-11 07:41:08

```

### ISO
在时间日期上它全称是ISO 8601，是一种日期/时间表示方法的规范。规定了一种明确的、国际上都能理解的日历和时钟格式。


这一ISO标准有助于消除各种日-日惯例、文化和时区对全球业务产生的影响。它提供了一种显示日期和时间的方式，这种方式是明确定义的，对人和机器都是可以理解的。当日期用数字表示时，它们可以以不同的方式进行解释。例如，01/05/12可以表示2012年1月5日或2012年5月1日。在个人层面上，这种不确定性可能非常令人沮丧，在商业环境中，它可能非常昂贵。在日期不明确的情况下，组织会议和交付、书写合同和购买机票都是非常困难的。

ISO 8601通过制定一种国际公认的日期表示方式来解决这种不确定性：YYYY-MM-DD。例如 September 27, 2012就会被表示为2012-09-27。

很多开发语言内置了一些常用的ISO标准日期/时间格式，如Java中的：
```
ISO.DATE：yyyy-MM-dd, e.g. "2000-10-31"
ISO.TIME：HH:mm:ss.SSSXXX, e.g. "01:30:00.000-05:00"
ISO.DATE_TIME：yyyy-MM-dd'T'HH:mm:ss.SSSXXX, e.g. "2000-10-31T01:30:00.000-05:00".
```

### 夏令时
DST（Daylight Saving Time），夏令时又称夏季时间（可没有冬令时哦）。它是为节约能源而人为规定地方时间的制度（鼓励人们早睡早起，不要浪费电，夏天日照时间长尽量多用自然资源），全球约40%的国家在夏季使用夏令时，其他国家则全年只使用标准时间。正在使用夏令时的代表国家：美国、欧盟、俄罗斯等等。

每年的夏令时时间段还不一样（一般在3月的第2个周日开始），比如美国2020年夏令时时间是：2020年3月8日 - 2020年11月1日。具体做法是：在3.8号这天将时钟往前拨拨1个小时，11.1号这天还原回来。

❝ 
中国在1986 - 1992年短暂搞过一段时间，但太麻烦就“废弃”了

❞
大事记：目前全世界有近110个国家每年要实行夏令时。自2011年3月27日开始俄罗斯永久使用夏令时，把时间拨快一小时，不再调回。