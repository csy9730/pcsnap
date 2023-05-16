import argparse
import time
import logging
import sys
import os
import datetime as dt
from typing import List

from sqlalchemy import Column, String, Integer, create_engine, Boolean, Float, DateTime, Enum, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.schema import ForeignKey  # , relationship
from pcsnap.flactodol import datetimestr_2_dt

import socket

def printUserMac():
    import getpass
    print(getpass.getuser(), getpass.getpass,os.getlogin(), socket.gethostname())


def getLogger(name, level="INFO", disable=False, log_file="flactodol.log"):
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


def gen_db_path(pth:str):
    DB = 'sqlite:///%s/flactodol.db' % pth
    DB = DB.replace('\\', '/')
    return DB


def get_all_config_path() -> List[str]:
    return [os.path.join(os.getcwd(), '.pcsnap'), os.path.join(os.path.dirname(os.path.abspath(__file__)), '.pcsnap'), os.path.expanduser('~/.pcsnap'), '/etc/pcsnap']


def find_config_path():
    ff = get_all_config_path()
    for f in ff:
        if os.path.isdir(f):
            return f
    return ff[-2]

def new_get_conffile(pfn:str):
    import configparser
    _conf = configparser.ConfigParser()
    _conf.read(pfn)
    # print(_conf.sections())
    if not _conf.sections():
        DB = gen_db_path(os.path.expanduser('~/.pcsnap'))
        LOG_FILE = os.path.expanduser('~/.pcsnap/flactodol.log')
        import pcsnap
        import platform
        dct = {
            "default": {
                "created_at": time.strftime('%Y-%m-%d %H:%M:%S'), 
                "author": os.getlogin(), 
                "agent": ' '.join(['pcsnap', 'flactodol', pcsnap.__version__, 'python', platform.python_version(), platform.system(), platform.version(), platform.machine()]), 
                "log_file": LOG_FILE, 
                "database": DB,
                "hostname": socket.gethostname(),
                "user_id": 0
            }
        }
        _conf.read_dict(dct)   
        _conf.write(open(pfn, 'w'))
    else:
        dct = {"default": {"visited_at": time.strftime('%Y-%m-%d %H:%M:%S')}}
        _conf.read_dict(dct)   
        _conf.write(open(pfn, 'w'))
    return _conf

Base = declarative_base()

pth = os.path.expanduser('~/.pcsnap')
os.makedirs(pth, exist_ok=True)
pfn = os.path.join(find_config_path(), "flactodol.ini")
conf = new_get_conffile(pfn)
DB = conf.get('default', 'database')
LOG_FILE = conf.get('default','log_file')
logger = getLogger(__name__, log_file=LOG_FILE)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(80), unique=True, nullable=False)
    password = Column(LargeBinary(128), nullable=True)
    created_at = Column(DateTime,
                           nullable=False,
                           default=dt.datetime.now)
    is_active = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    first_name = Column(String(30), nullable=True)
    last_name = Column(String(30), nullable=True)

    def __repr__(self):
        return '<User %s %s>' % (self.id, self.username)


class Todos(Base):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True)

    name = Column(String(60))
    about = Column(String(660), nullable=True)
    useragent = Column(String(60))

    status = Column(Boolean, default=False) # is_close
    is_success = Column(Boolean, default=False)
    is_active = Column(Boolean(), default=True)

    # progress = Column(Integer, default=0)
    tag = Column(Enum('weekly', 'work', 'study', 'relax', 'self', 'event'),
                    server_default='weekly',
                    nullable=False)

    created_at = Column(DateTime,
                           nullable=False,
                           default=dt.datetime.now)
    updated_at = Column(DateTime,
                           nullable=False,
                           default=dt.datetime.now)

    verb_tag = Column(Enum('code', 'tool', 'solve', 'apply', 'weekly', 'misc', 'doc', 'read', 'relax', 'law', 'log'),
                    server_default='misc',
                    nullable=False)

    user_id = Column(Integer, ForeignKey('users.id'))

    is_project = Column(Boolean(), default=False)
    par_id = Column(Integer, ForeignKey('todos.id'), nullable=True)
    depend_id = Column(Integer, ForeignKey('todos.id'), nullable=True)
    
    plan_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)

    stage = Column(Enum('new', 'ss', 'design', 'do', 'log'),
                server_default='new',
                nullable=False)
    progress = Column(Integer, default=0)

    plan_hour = Column(Integer, nullable=True)
    used_hour = Column(Integer, nullable=True)
    
    def __init__(self, **kwargs):
        if "updated_at" in kwargs:
            updated_at = kwargs.pop("updated_at")
            if isinstance(updated_at, str):
                self.updated_at = dt.datetime.strptime(updated_at,'%Y-%m-%d %H:%M:%S')
            else:
                self.updated_at = updated_at
        super(Todos, self).__init__(**kwargs)

    def __repr__(self):
        return '<Todos %s %s %s %s %s>' % (self.id, self.name, self.is_open, self.is_done, self.tag)

    def to_dict(self):
        KEYS = ('id', "name", "status", "progress", "tag", "about", "is_success", \
            "verb_tag", "is_project", "par_id", "stage", "is_active", "depend_id")
        
        dct = {k:v for k, v in self.__dict__.items() if k in KEYS}
        dct["created_at"] = self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        dct["updated_at"] = self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        return dct

    def from_dict(self, dat):
        self.updated_at = dt.datetime.now()
        for k, v in dat.items():
            if k in ["updated_at"]:
                setattr(self, k, dt.datetime.strptime(v,'%Y-%m-%d %H:%M:%S')) 
            elif k != 'id':
                setattr(self, k, v)

    def update_plan(self):
        if not self.is_active and self.plan_at and (self.plan_at > dt.datetime.now()):
            self.is_active = True

    @staticmethod
    def genDefaultJson(par_id=0):
        todo = {'name': "", 'status': False, 'progress': 0, 'tag':'weekly', 'about':"",\
            "is_success": False, "created_at":"", "updated_at": dt.datetime.now(), "verb_tag": "misc", \
            "is_project": False, "stage": "new", "is_active": True}

        if par_id:
            par = Todos.query.filter_by(id=par_id).first()
            if par:
                todo['tag'] = par.tag
                todo['verb_tag'] = par.verb_tag
                todo['par_id'] = par_id
        return todo

    @property
    def is_done(self):
        return "done" if self.is_success else "fail"

    @property
    def is_open(self):
        return "open" if self.status else "closed"     
    
def initDb(args):
    engine = create_engine(DB)
    # engine = create_engine('sqlite:///foo.db?check_same_thread=False', echo=True)
    # if not os.path.exists('data.sqlite'):
    #     db.create_all()
    # # db.drop_all()
    logger.info(DB)
    Base.metadata.create_all(engine, checkfirst=True)
    return engine

def get_session():
    engine = create_engine(DB)
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    return session


def showDb(args):
    session = get_session()
    if args.word == 'user':
        lst = session.query(User).order_by(User.created_at.desc()).limit(args.page_size)
        for s in lst:
            print(s.id, s.username, s.created_at)

    elif args.word == 'all':
        lst = session.query(Todos).order_by(Todos.updated_at.desc()).limit(args.page_size)
        for s in lst:
            print(s.id, s.name, s.tag, s.verb_tag, s.is_done, s.created_at)

    elif args.word == 'task':
        lst = session.query(Todos).filter_by(status=False).order_by(Todos.updated_at.desc()).limit(args.page_size)
        for s in lst:
            print(s.id, s.name, s.tag, s.verb_tag, s.is_done, s.created_at)

    elif args.word == 'todo':
        lst = session.query(Todos).filter_by(status=False, is_active=True, is_project=False).order_by(Todos.updated_at.desc()).limit(args.page_size)
        for s in lst:
            print(s.id, s.name, s.tag, s.verb_tag, s.is_done, s.created_at)

    elif args.word == 'plan':
        lst = session.query(Todos).filter_by(status=False, is_active=False, is_project=False).order_by(Todos.updated_at.desc()).limit(args.page_size)
        for s in lst:
            print(s.id, s.name, s.tag, s.verb_tag, s.is_done, s.created_at)

    elif args.word == 'project':
        lst = session.query(Todos).filter_by(status=False, is_project=True).order_by(Todos.updated_at.desc()).limit(args.page_size)
        for s in lst:
            print(s.id, s.name, s.tag, s.verb_tag, s.is_done, s.created_at)

    elif args.word == 'done':
        lst = session.query(Todos).filter_by(status=True).filter_by(is_success=True).order_by(Todos.updated_at.desc()).limit(args.page_size)
        for s in lst:
            # _dt = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(s.created_at))
            print(s.id, s.name, s.tag, s.verb_tag, s.is_success, s.created_at)    

    elif args.word == 'fail':
        lst = session.query(Todos).filter_by(status=True).filter_by(is_success=False).order_by(Todos.updated_at.desc()).limit(args.page_size)
        for s in lst:
            # _dt = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(s.created_at))
            print(s.id, s.name, s.tag, s.verb_tag, s.is_done, s.created_at)   

    elif args.word == 'log':
        lst = session.query(Todos).filter_by(status=True).order_by(Todos.updated_at.desc()).limit(args.page_size)
        for s in lst:
            print(s.id, s.name, s.tag, s.verb_tag, s.is_done, s.created_at)  

"""
-all
    - task
        - todos
        - plan
        - project
    - log
        - done 
        - failed
"""

def addDb(args):
    # foo add -m "ladder plan" -t "work"
    session = get_session()

    # cnt = content.split(',')
    td = Todos(name=args.content, tag=args.tag, verb_tag=args.verb_tag, 
        useragent = conf.get('default', 'agent', fallback='flactodol'), 
        user_id = conf.getint('default','user_id'), par_id=args.par_id,
        created_at = datetimestr_2_dt(args.created_at)
    )
    session.add(td)
    session.commit()
    logger.info(td)

def addLogDb(args):
    session = get_session()

    # cnt = content.split(',')
    td = Todos(name=args.content, tag=args.tag, verb_tag=args.verb_tag, 
        useragent = conf.get('default', 'agent', fallback='flactodol'), 
        user_id = conf.getint('default','user_id'), par_id=args.par_id,
        status=True, is_success=args.is_success,
        created_at = datetimestr_2_dt(args.created_at),
        # updated_at = datetimestr_2_dt(args.updated_at),
    )
    session.add(td)
    session.commit()
    logger.info(td)

def addPlanDb(args):
    session = get_session()

    # cnt = content.split(',')
    td = Todos(name=args.content, tag=args.tag, verb_tag=args.verb_tag, 
        useragent = conf.get('default', 'agent', fallback='flactodol'), 
        user_id = conf.getint('default','user_id'),par_id=args.par_id,
        depend_id=args.depend_id, is_active=False,
        created_at = datetimestr_2_dt(args.created_at),
    )
    session.add(td)
    session.commit()
    logger.info(td)

def addProjectnDb(args):
    session = get_session()

    # cnt = content.split(',')
    td = Todos(name=args.content, tag=args.tag, verb_tag=args.verb_tag, 
        useragent = conf.get('default', 'agent', fallback='flactodol'), 
        user_id = conf.getint('default','user_id'),par_id=args.par_id,
        created_at = datetimestr_2_dt(args.created_at)
    )
    session.add(td)
    session.commit()
    logger.info(td)

def infoDb(args):
    session = get_session()
    td = session.query(Todos).filter_by(id=args.id).first()
    if not td:
        logger.waning("Todo {} doesn't exist".format(args.id))
    logger.info(td)
    if td.is_project:
        tds = session.query(Todos).filter_by(par_id=args.id).all()
        for s in tds:
            print(s.id, s.name, s.tag, s.verb_tag, s.is_done, s.created_at, td.is_project)
    else:
        print(td.id, td.name, td.tag, td.verb_tag, td.is_done, td.created_at, td.is_project)
        if td.par_id:
            tdp = session.query(Todos).filter_by(id=td.par_id).all()
            for s in tdp:
                print(s.id, s.name, s.tag, s.verb_tag, s.is_done, s.created_at, td.is_project)


def finishDb(args):
    session = get_session()
    td = session.query(Todos).filter_by(id=args.id).first()
    if not td:
        logger.waning("Todo {} doesn't exist".format(args.id))
    td.status = True
    td.is_success = True
    td.is_active = True
    session.add(td)
    logger.info(td)
    tds = session.query(Todos).filter_by(depend_id=args.id, is_active=False).all()
    logger.debug(tds)
    for t in tds:  
        t.is_active = True
        session.add(t)
    session.commit()

def unfinishDb(args):
    engine = create_engine(DB)
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    td = session.query(Todos).filter_by(id=args.id).first()

    if not td:
        logger.waning("Todo {} doesn't exist".format(args.id))
    td.status = True
    td.is_success = False
    logger.info(td)
    session.add(td)
    session.commit()


def serveDb(args):
    pass

def parse_args(cmd=None):
    import argparse
    parser = argparse.ArgumentParser(description='')
    # parser.add_argument('--gpu-on',default = False,action="store_true",help ="flag to use gpu ,default to use cpu")
    subparsers = parser.add_subparsers(help='sub-command help')
    parserT = subparsers.add_parser('init', help='init database')
    parserT.set_defaults(handle=initDb)

    parserA = subparsers.add_parser('add', help='fill data to database')
    parserA.add_argument('content')
    parserA.add_argument('--tag', '-t', default='weekly', choices=['weekly', 'work', 'study', 'relax', 'self', 'event'])
    parserA.add_argument('--verb-tag', '-vb', default='weekly', choices=['code', 'tool', 'solve', 'apply', 'weekly', 'misc', 'doc', 'read', 'relax', 'law', 'log'])
    parserA.add_argument('--about')
    parserA.add_argument('--created-at', '-ct')
    parserA.add_argument('--is-project', '-ip', action='store_true')
    parserA.add_argument('--par-id', type=int)
    # parserA.add_argument('--finish-at')

    parserA.set_defaults(handle=addDb)

    parserAl = subparsers.add_parser('addlog', help='fill data to database')
    parserAl.add_argument('content')
    parserAl.add_argument('--tag', '-t', default='weekly', choices=['weekly', 'work', 'study', 'relax', 'self', 'event'])
    parserAl.add_argument('--verb-tag', '-vb', default='weekly', choices=['code', 'tool', 'solve', 'apply', 'weekly', 'misc', 'doc', 'read', 'relax', 'law', 'log'])
    parserAl.add_argument('--about')
    parserAl.add_argument('--created-at', '-ct')
    parserAl.add_argument('--is-project', '-ip', action='store_true')
    parserAl.add_argument('--is-success', '-is', action='store_true', default=True)
    parserAl.add_argument('--is-fail', '-if', action='store_false', dest='is_success')
    parserAl.add_argument('--par-id', type=int)
    parserAl.set_defaults(handle=addLogDb)

    parserAp = subparsers.add_parser('addplan', help='fill data to database')
    parserAp.add_argument('content')
    parserAp.add_argument('--tag', '-t', default='weekly', choices=['weekly', 'work', 'study', 'relax', 'self', 'event'])
    parserAp.add_argument('--verb-tag', '-vb', default='weekly', choices=['code', 'tool', 'solve', 'apply', 'weekly', 'misc', 'doc', 'read', 'relax', 'law', 'log'])
    parserAp.add_argument('--about')
    parserAp.add_argument('--created-at', '-ct')
    parserAp.add_argument('--plan-at', '-pt')
    parserAp.add_argument('--is-project', '-ip', action='store_true')
    parserAp.add_argument('--par-id', type=int)
    parserAp.add_argument('--depend-id', type=int)
    parserAp.set_defaults(handle=addPlanDb)

    parserAj = subparsers.add_parser('addproject', help='fill data to database')
    parserAj.add_argument('content')
    parserAj.add_argument('--tag', '-t', default='weekly', choices=['weekly', 'work', 'study', 'relax', 'self', 'event'])
    parserAj.add_argument('--verb-tag', '-vb', default='weekly', choices=['code', 'tool', 'solve', 'apply', 'weekly', 'misc', 'doc', 'read', 'relax', 'law', 'log'])
    parserAj.add_argument('--about')
    parserAj.add_argument('--created-at', '-ct')
    parserAj.add_argument('--is-project', '-ip', action='store_true')
    parserAj.add_argument('--par-id', type=int)
    parserAj.set_defaults(handle=addProjectnDb)

    parserS = subparsers.add_parser('show', help='show database')
    parserS.add_argument('--word', '-w', default='todo', choices=['user', 'all', 'task', 'todo', 'done', 'fail', 'plan', 'log', 'project'])
    parserS.add_argument('--page-size', '-ps', type=int, default=10)
    parserS.add_argument('--offset', type=int, default=0)
    #  .offset((page_index-1)*page_size)
    parserS.set_defaults(handle=showDb)

    parserFo = subparsers.add_parser('info', help='info to to database')
    parserFo.add_argument('id', type=int)
    parserFo.set_defaults(handle=infoDb)

    parserF = subparsers.add_parser('finish', help='finished to to database')
    parserF.add_argument('id', type=int)
    parserF.set_defaults(handle=finishDb)

    parserU = subparsers.add_parser('unfinish', help='unfinished data to database')
    parserU.add_argument('id', type=int)
    parserU.set_defaults(handle=unfinishDb)

    parserH = subparsers.add_parser('serve', help='serve that can watch or show')
    parserH.set_defaults(handle=serveDb)

    args = parser.parse_args(cmd)
    if not hasattr(args, 'handle'):
        parser.print_help()

    return args

def main(cmd=None):
    args = parse_args(cmd)
    # print(args)
    if hasattr(args, 'handle'):
        args.handle(args) 

if __name__ == "__main__":
    main()