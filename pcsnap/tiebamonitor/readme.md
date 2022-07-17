# readme



- 查询所有用户   /users
- 查询所有帖子   /tiezi
- 查询所有回帖记录 /tielogs

- 每天新增发帖数  /tiezi/today/new
    - 每月新增发帖 /tiezi/week/new
    - 每季度新增发帖 /tiezi/quarter/new
    - 去年每个月的发帖数 /tiezi/1year_month/count
    - 每年新增发帖
- 每天新增回帖数 去除抽奖导致的极大值
    - 每月新增回帖数 /tielogs/month/count
    - 每季度新增回帖数
    - 每年新增回帖数
- 查询指定帖子的所有回帖记录  /tiezi/id/tielogs
- 查询回帖记录最多的top帖子
    - 每月top贴  /tiezi/month/top_pointNum
    - 快照 /tiezilog/month/group_tie/top_pointNum
    - 精品判断
    - nlp分析
        - top帖子标题分析 词云
        - 情感分析

- 每天新增用户数
    - 月活跃用户数
    - 周活跃用户数
- 查询指定用户 /user/id/
- 查询指定用户的所有发帖 /user/id/post
- 查询指定用户的所有回帖 /user/id/reply
- 查询发帖记录最多的top用户
    - 每天 /user/tiezi/top_count_post
    - 每月
- 查询回帖记录最多的top用户
    - 每天
    - 每月
- 查询发帖回复累计最多的top用户
    - 每周
    - 每月
- 查询指定用户的所有发帖


/tiezi/main_tag/time_tag/

### 时间筛选

时间表达方式
- hour 这个小时内
- 1hour 上一个1小时之前
- 24hour 24小时内
- today 今天
- 1day 昨天
- 2day 前天
- 3day 三天前
- 7day 7天内
- week 这周
- 1week 上周
- 2week
- month
- 1month
- 2month
- quarter
- 1quarter
- 2quarter
- 3quarter
- year
- 1year

```
    if timetag.endswith('today'):
        tm = dt.timedelta(days=0)
    elif timetag.endswith('week'):
        tm = dt.timedelta(weeks=1)
    elif timetag.endswith('month'):
        tm = dt.timedelta(days=30)
    elif timetag.endswith('quarter'):
        tm = dt.timedelta(days=91)
    elif timetag.endswith('year'):
```


python tiebaMonitor.py watch -l -itv 1200 -kw python -kw 2ch -kw dota -kw 游戏王ygocore -kw 上位卡组 -kw 比亚迪 -kw 清华大学 -kw 广州 -kw 中华城市 -kw 华南理工大学 -kw bilibili -kw wow
