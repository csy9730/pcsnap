# misc

## request 

匿名访问的tieba的结构和 cookie访问的结果不同
需要小心处理。



## group_by + first/count
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