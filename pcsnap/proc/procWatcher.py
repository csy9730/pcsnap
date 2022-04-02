import time
import psutil
import json
import logging
import sys
import os

from sqlalchemy import Column, String, Integer, create_engine, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.schema import ForeignKey  # , relationship


Base = declarative_base()
pth = os.path.expanduser('~/.pcsnap')
os.makedirs(pth, exist_ok=True)
DB = 'sqlite:///%s/tasklists.db' % pth
DB = DB.replace('\\', '/')
# DB = 'sqlite://C:/Users/foo/.pcsnap/tasklists.db' error
# DB = 'sqlite:///C:/Users/foo/.pcsnap/tasklists.db'
# print(DB)
# exit(0)

def getLogger(name, level="INFO", disable=False, log_file="tmp.log"):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.disabled = disable
    if not logger.handlers:
        handler = logging.FileHandler(log_file)
        handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))  # create a logging format
        logger.addHandler(handler)  # add the handlers to the logger
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))  # create a logging format
        logger.addHandler(console)
    return logger

logger = getLogger(__name__)

class Exe(Base):
    __tablename__ = 'exes'
    id = Column(Integer, primary_key=True)
    name = Column(String(60))
    procs = relationship("Process", backref='exe', lazy='dynamic')

    def __repr__(self):
        return '<Exe %s %s>' % (self.id, self.name)


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
    num_threads = Column(Integer, nullable=True)
    read_count = Column(Integer, nullable=True)
    write_count = Column(Integer, nullable=True)
    inet = Column(Integer, nullable=True)

    def __repr__(self):
        return '<Processlog %s %s>' % (self.proc.name, self.datetime)


def addProcessLog(DBSession, tasklist):
    session = DBSession()
    qAlv = session.query(Process).filter_by(is_live=True)
    alvs = qAlv.all()
    for s in alvs:
        s.is_live = False
    logger.info(len(alvs))
    # print(len(qAlv.all()))

    dt = int(time.time())
    for s in tasklist:
        try:
            exe = s.exe()
            fExe = session.query(Exe).filter_by(name=exe).first()
            if not fExe:
                fExe = Exe(name=exe)
                session.add(fExe)

            ctm = int(s.create_time())
            ppid = s.ppid()
            fProc = session.query(Process).filter_by(pid=s.pid, ppid=ppid, create_time=ctm).first()  # exe=s.exe(), 
            if not fProc:    
                fProc = Process(pid=s.pid, ppid=ppid, name=s.name(), cmdline=json.dumps(s.cmdline()), cwd=s.cwd(), is_live=True, create_time=ctm)
                session.add(fProc)

            io_cnt = s.io_counters()
            read_count = io_cnt.read_count
            write_count = io_cnt.write_count
            
            pl = Processlog(update_time=dt, use_cpu=int(s.cpu_percent()*1000), use_mem=int(s.memory_percent()*1000),
                 num_threads=s.num_threads(), read_count=read_count,write_count=write_count, inet=len(s.connections()))
            fProc.is_live = True
            fExe.procs.append(fProc)
            fProc.logs.append(pl)
            session.add(fProc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            # logger.error(s)

    session.commit()


def initDb(args):
    engine = create_engine(DB)
    # engine = create_engine('sqlite:///foo.db?check_same_thread=False', echo=True)
    # if not os.path.exists('data.sqlite'):
    #     db.create_all()
    # # db.drop_all()
    logger.info(DB)
    Base.metadata.create_all(engine, checkfirst=True)
    return engine


def watchDb(args):
    engine = create_engine(DB)
    DBSession = sessionmaker(bind=engine)
    if args.loop:
        while 1:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),end='\t')
            addProcessLog(DBSession, psutil.process_iter(['pid', 'ppid', 'cmdline', 'name', 'username']))
            time.sleep(args.interval)
    else:
        addProcessLog(DBSession, psutil.process_iter(['pid', 'ppid', 'cmdline', 'name', 'username']))


def showDb(args):
    engine = create_engine(DB)
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    if args.word == 'proc':
        lst = session.query(Process).order_by(Process.create_time.desc()).limit(args.page_size)
        for s in lst:
            _dt = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(s.create_time))
            print(s.pid, s.exe.name, _dt)
    elif args.word == 'live_proc':
        lst = session.query(Process).filter_by(is_live=True).order_by(Process.create_time.desc()).limit(args.page_size)
        for s in lst:
            _dt = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(s.create_time))
            print(s.pid, s.exe.name, _dt)
    elif args.word == 'dead_proc':
        lst = session.query(Process).filter_by(is_live=False).order_by(Process.create_time.desc()).limit(args.page_size)
        for s in lst:
            _dt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            print(s.pid, s.exe.name, _dt)
        # print(lst)
        # session.query(Exe).filter_by(exe=exe).first()
    elif args.word == 'exe':
        lst = session.query(Exe).order_by(Exe.id.desc()).limit(args.page_size)
        for s in lst:
            # _dt = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(s.create_time))
            print(s.id, s.name)
    elif args.word == 'log':
        lst = session.query(Processlog).order_by(Processlog.update_time.desc()).limit(args.page_size)
        print('id,pid,name,cpu,mem,reads,writes,inet,datetime')
        for s in lst:
            _dt = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(s.update_time))
            print(s.id, s.proc.pid, s.proc.name, s.use_cpu, s.use_mem, s.read_count, s.write_count, s.inet, _dt)
    elif args.word == 'summary':
        print("summary")
    else:
        print("else")
    session.close()
    # procs

"""
    最高访问次数的exe， 全部/当天/当月
    最高存活时间的exe， 全部/当天/当月

    最近打开的进程
    最近关闭的进程


    top 10 / sorter
        /  filter
        / grouper


"""

def parse_args(cmd=None):
    import argparse
    parser = argparse.ArgumentParser(description='')
    # parser.add_argument('--gpu-on',default = False,action="store_true",help ="flag to use gpu ,default to use cpu")
    subparsers = parser.add_subparsers(help='sub-command help')
    parserT = subparsers.add_parser('init', help='init database')
    parserT.set_defaults(handle=initDb)

    parserW = subparsers.add_parser('watch', help='fill data to database')
    parserW.add_argument('--loop', '-l', action='store_true')
    parserW.add_argument('--interval', '-itv', type=int, default=600, help='loop interval default(300) second')
    parserW.set_defaults(handle=watchDb)

    parserS = subparsers.add_parser('show', help='show database')
    parserS.add_argument('--word', default='proc', choices=['proc', 'exe', 'log', 'summary'])
    parserS.add_argument('--page-size', '-ps', type=int, default=10)
    parserS.add_argument('--offset', type=int, default=0)
    #  .offset((page_index-1)*page_size)
    parserS.set_defaults(handle=showDb)

    args = parser.parse_args(cmd)
    if not hasattr(args, 'handle'):
        parser.print_help()

    return args


def main(cmd=None):
    args = parse_args(cmd)
    if hasattr(args, 'handle'):
        args.handle(args) 


if __name__ == "__main__":
    # sqlDemo()
    main()
