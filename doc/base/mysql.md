# mysql


### utf8保存emoji出现乱码
* mysql 用utf8 保存 emoji，出现乱码，无法处理
mysql服务端的utf8编码占3个字节(即utf8mb3)，而emoji表情占4个字节。故存储包含emoji表情的文本时要在服务端使用utf8mb4编码。

**A**: 
1. 执行字符集设置语句: `set names utf8mb4`
2. 过滤脏字符 
3. base64 转码



#### base64 转码
``` python
import base64
def b64encode(s):
    return base64.b64encode(s)
import jinja2

jinja2.environment.filters['b64encode'] = b64encode
```
