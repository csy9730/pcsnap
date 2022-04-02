# sqlite

``` python

def sqlDemo():
    def createDb():
        engine = create_engine(DB)
        # engine = create_engine('sqlite:///foo.db?check_same_thread=False', echo=True)
        # if not os.path.exists('data.sqlite'):
        #     db.create_all()
        # # db.drop_all()
        Base.metadata.create_all(engine, checkfirst=True)
        return engine

    def insertData(DBSession):
        session = DBSession()
        a_user = Process(name='Allice', pid=2)
        session.add(a_user)
        session.commit()
        session.close()

    def insertData2(DBSession):
        session = DBSession()
        a_user = Process(name='Caddy', pid=13)
        a_log = Processlog(use_cpu=5)
        a_user.logs.append(a_log)
        session.add(a_log)
        session.add(a_user)
        session.commit()
        session.close()

    def queryData(DBSession):
        # 字符串匹配方式筛选条件 并使用 order_by进行排序
        session = DBSession()
        r6 = session.query(Process).all()
        print(r6)
        session.close()

    def queryData2(DBSession):
        # 字符串匹配方式筛选条件 并使用 order_by进行排序
        session = DBSession()
        r = session.query(Process).all()
        print(r)
        r6 = session.query(Processlog).all()
        print(r6)
        session.close()

    engine = createDb()
    DBSession = sessionmaker(bind=engine)
    insertData(DBSession)
    queryData2(DBSession)
```



"""
外键/表关系都是虚的，不会实际反映到数据库表上。
ForeignKey 描述列对应别的表的id列。
relationship 可以描述两个表的关系，因为表关系对偶，只要可以准确描述对应的外键id，可以把关系语句放到表1或表2.
注意： 1对多关系时，可以添加 lazy='dynamic'选项， 多对一关系，不能配置lazy='dynamic'选项。

正向查询： 从多所在的表格查询 1所在的表格，
反向查询： 从一所在的表格查询 多所在的表格（因为会返回列表，所以需要注意性能）
"""


## path
``` python
pth = os.path.expanduser('~/.pcsnap')
os.makedirs(pth, exist_ok=True)
DB = 'sqlite:///%s/tasklists.db' % pth
DB = DB.replace('\\', '/')
# DB = 'sqlite://C:/Users/foo/.pcsnap/tasklists.db' # error
DB = 'sqlite:///C:/Users/foo/.pcsnap/tasklists.db'

DB = "sqlite:///C:\\Users\\Username\\AppData\\Roaming\\Appname\\mydatabase.db"
```
