# select


### sql清空表数据
一、sql清空表数据的三种方式：

1、truncate--删除所有数据，保留表结构，不能撤销还原

2、delete--是逐行删除速度极慢，不适合大量数据删除

3、drop--删除表，数据和表结构一起删除，快速

二、语法

truncate table 表名

delete from 表名

delete from 表名 where 列名="value "

drop form 表名

### Unknown database
**Q**: sqlalchemy.exc.OperationalError: (pymysql.err.OperationalError) (1049, "Unknown database abc

**A**:  手动在mysql 中创建database abc 。

### group_by + first/count
``` python
session.query(func.count(User.id)).\
        group_by(User.name)

len(Tiezilog.query.group_by('tiezi_id').all())

db.session.query(func.count(Tiezilog.id)).group_by(Tiezilog.tiezi_id)

cnt = db.session.query(func.count(Tiezilog.id)).group_by(Tiezilog.tiezi_id).all()

db.session.query(func.max(Tiezilog.pointNum), Tiezilog).group_by(Tiezilog.tiezi_id).all()
```

``` python
sess = obtain_session()
records = sess.query(Pageview.post_id,
                     func.count(Pageview.post_id).label('count')).
                     filter(Pageview.date_posted.between('2019-10-01', '2019-10-14')).
                     group_by(Pageview.post_id).order_by('count').desc()
```

[https://hakibenita.com/sql-group-by-first-last-value](https://hakibenita.com/sql-group-by-first-last-value)

[https://stackoverflow.com/questions/3800551/select-first-row-in-each-group-by-group](https://stackoverflow.com/questions/3800551/select-first-row-in-each-group-by-group)