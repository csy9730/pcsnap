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
