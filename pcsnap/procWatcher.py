from sqlalchemy import Column, String, Integer, create_engine, Boolean,Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.schema import ForeignKey  # , relationship
import time
import psutil
import json
Base = declarative_base()


"""
外键/表关系都是虚的，不会实际反映到数据库表上。
ForeignKey 描述列对应别的表的id列。
relationship 可以描述两个表的关系，因为表关系对偶，只要可以准确描述对应的外键id，可以把关系语句放到表1或表2.
注意： 1对多关系时，可以添加 lazy='dynamic'选项， 多对一关系，不能配置lazy='dynamic'选项。

正向查询： 从多所在的表格查询 1所在的表格，
反向查询： 从一所在的表格查询 多所在的表格（因为会返回列表，所以需要注意性能）
"""
class Exe(Base):
    __tablename__ = 'exes'
    id = Column(Integer, primary_key=True)
    exe = Column(String(60))
    procs = relationship("Process", backref='exe', lazy='dynamic')
    def __repr__(self):
        return '<Exe %s_%s %s>' % (self.id, self.exe)

class Process(Base):
    __tablename__ = 'process'
    id = Column(Integer, primary_key=True)
    name = Column(String(40), nullable=True)
    pid = Column(Integer, nullable=True)
    ppid = Column(Integer, nullable=True)
    cmdline = Column(String(40), nullable=True)
    cwd = Column(String(40), nullable=True)
    is_live = Column(Boolean, default=True)
    is_app = Column(Boolean, default=True)
    create_time = Column(Integer, nullable=True)
    # logs = relationship("Processlog")
    logs = relationship("Processlog", backref='proc', lazy='dynamic')
    exe_id = Column(Integer, ForeignKey("exes.id"))

    def __repr__(self):
        return '<Process %s_%s %s>' % (self.id, self.pid, self.name)


class Processlog(Base):
    __tablename__ = 'processlog'
    id = Column(Integer, primary_key=True)
    update_time = Column(Integer, nullable=True)
    use_cpu = Column(Integer, nullable=True)
    use_mem = Column(Integer, nullable=True)
    proc_id = Column(Integer, ForeignKey("process.id"))

    def __repr__(self):
        return '<Processlog %s %s>' % (self.proc.name, self.datetime)


def addProcessLog(DBSession, tasklist):
    session = DBSession()
    qAlv = session.query(Process).filter_by(is_live=True)
    alvs = qAlv.all()
    for s in alvs:
        s.is_live = False
    print(len(alvs))
    # print(len(qAlv.all()))

    dt = int(time.time())
    for s in tasklist:
        try:
            exe= s.exe()
            fExe = session.query(Exe).filter_by(exe=exe).first()
            if not fExe:
                fExe = Exe(exe=exe)
                session.add(fExe)

            ctm = int(s.create_time())
            ppid = s.ppid()
            fProc = session.query(Process).filter_by(pid=s.pid, ppid=ppid, create_time=ctm).first()  # exe=s.exe(), 
            if not fProc:    
                fProc = Process(pid=s.pid, ppid=ppid, name=s.name(), cmdline=json.dumps(s.cmdline()), cwd=s.cwd(), is_live=True, create_time=ctm)
                session.add(fProc)
            
            pl = Processlog(update_time=dt)
            fProc.is_live = True
            fExe.procs.append(fProc)
            fProc.logs.append(pl)
            session.add(fProc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            print(s)

    session.commit()


def main():
    engine = createDb()
    DBSession = sessionmaker(bind=engine)
    addProcessLog(DBSession, psutil.process_iter(['pid', 'ppid', 'cmdline', 'name', 'username']))
    

def psutilDemo():
    p = psutil.Process()
    for proc in psutil.process_iter(['pid', 'ppid', 'cmdline', 'name', 'username']):
        print(proc.pid)
    # p.as_dict().keys()
    # dict_keys(['nice', 'open_files', 'cpu_affinity', 'threads', 'environ', 'username', 'cmdline', 'memory_full_info', 'num_handles', 'ionice', 'num_ctx_switches', 'io_counters', 'cpu_times', 'num_threads', 'status', 'exe', 'memory_percent', 'pid', 'memory_maps', 'cwd', 'name', 'create_time', 'cpu_percent', 'connections', 'memory_info', 'ppid'])
    """
    with p.oneshot():
        p.name()  # execute internal routine once collecting multiple info
        p.cpu_times()  # return cached value
        p.cpu_percent()  # return cached value
        p.create_time()  # return cached value
        p.ppid()  # return cached value
        p.status()  # return cached value
        p.cmdline()
    """

def createDb():
    engine = create_engine('sqlite:///tasklists.db')
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


def queryData(session):
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

def sqlDemo():
    engine = createDb()
    DBSession = sessionmaker(bind=engine)
    insertData(DBSession)
    queryData2(DBSession)


"""
49
157
157
74kb => 80kb
"""
if __name__ == "__main__":
    # sqlDemo()
    main()

