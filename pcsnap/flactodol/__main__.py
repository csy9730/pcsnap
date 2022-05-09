import argparse
import time
import psutil
import json
import logging
import sys
import os
import datetime as dt

from sqlalchemy import Column, String, Integer, create_engine, Boolean, Float, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.schema import ForeignKey  # , relationship


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


def gen_db_path(pth):
    DB = 'sqlite:///%s/flactodol.db' % pth
    DB = DB.replace('\\', '/')
    return DB


def get_all_config_path():
    return [os.path.join(os.getcwd(), '.pcsnap'), os.path.join(os.path.dirname(os.path.abspath(__file__)), '.pcsnap'), os.path.expanduser('~/.pcsnap'), '/etc/.pcsnap']


def find_config_path():
    ff = get_all_config_path()
    for f in ff:
        if os.path.isdir(f):
            return f
    return ff[-2]

def new_get_conffile(pfn):
    import configparser
    _conf = configparser.ConfigParser()
    _conf.read(pfn)
    # print(_conf.sections())
    if not _conf.sections():
        DB = gen_db_path(os.path.expanduser('~/.pcsnap'))
        LOG_FILE = os.path.expanduser('~/.pcsnap/flactodol.log')
        dct = {"default": {"created_at": time.strftime('%Y-%m-%d %H:%M:%S'), "author": "foo", "agent": "pcsnap.proc", "log_file": LOG_FILE, "database": DB}}
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
    name = Column(String(60))
    # procs = relationship("Process", backref='exe', lazy='dynamic')

    def __repr__(self):
        return '<Exe %s %s>' % (self.id, self.name)


class Todos(Base):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True)
    name = Column(String(60))

    status = Column(Boolean, default=False)
    is_success = Column(Boolean, default=False)
    progress = Column(Integer, default=0)
    tag = Column(Enum('weekly', 'work', 'study', 'relax', 'self', 'event'),
                    server_default='weekly',
                    nullable=False)
    about = Column(String(660), nullable=True)
    created_at = Column(DateTime,
                           nullable=False,
                           default=dt.datetime.now)
    updated_at = Column(DateTime,
                           nullable=False,
                           default=dt.datetime.now)
    verb_tag = Column(Enum('code', 'tool', 'solve', 'apply', 'weekly', 'misc', 'doc', 'read', 'relax'),
                    server_default='misc',
                    nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))

    is_project = Column(Boolean(), default=False)
    par_id = Column(Integer, ForeignKey('todos.id'), nullable=True)

    is_active = Column(Boolean(), default=True)
    depend_id = Column(Integer, ForeignKey('todos.id'), nullable=True)
    plan_at = Column(DateTime, nullable=True)

    def __init__(self, **kwargs):
        if "updated_at" in kwargs:
            updated_at = kwargs.pop("updated_at")
            if isinstance(updated_at, str):
                self.updated_at = dt.datetime.strptime(updated_at,'%Y-%m-%d %H:%M:%S')
            else:
                self.updated_at = updated_at
        super(Todos, self).__init__(**kwargs)

    def __repr__(self):
        return '<Todos %s %s>' % (self.id, self.name)

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

def initDb(args):
    engine = create_engine(DB)
    # engine = create_engine('sqlite:///foo.db?check_same_thread=False', echo=True)
    # if not os.path.exists('data.sqlite'):
    #     db.create_all()
    # # db.drop_all()
    logger.info(DB)
    Base.metadata.create_all(engine, checkfirst=True)
    return engine

def addDb(args):
    pass

def showDb(args):
    pass

def finishDb(args):
    pass

def unfinishDb(args):
    pass

def serveDb(args):
    pass

def parse_args(cmd=None):
    import argparse
    parser = argparse.ArgumentParser(description='')
    # parser.add_argument('--gpu-on',default = False,action="store_true",help ="flag to use gpu ,default to use cpu")
    subparsers = parser.add_subparsers(help='sub-command help')
    parserT = subparsers.add_parser('init', help='init database')
    parserT.set_defaults(handle=initDb)

    parserA = subparsers.add_parser('addDb', help='fill data to database')
    parserA.add_argument('--loop', '-l', action='store_true')
    parserA.add_argument('--interval', '-itv', type=int, default=600, help='loop interval default(300) second')
    parserA.set_defaults(handle=addDb)

    parserS = subparsers.add_parser('show', help='show database')
    parserS.add_argument('--word', default='proc', choices=['proc', 'exe', 'log', 'summary'])
    parserS.add_argument('--page-size', '-ps', type=int, default=10)
    parserS.add_argument('--offset', type=int, default=0)
    #  .offset((page_index-1)*page_size)
    parserS.set_defaults(handle=showDb)

    parserF = subparsers.add_parser('finishDb', help='fill data to database')
    parserF.add_argument('--loop', '-l', action='store_true')
    parserF.add_argument('--interval', '-itv', type=int, default=600, help='loop interval default(300) second')
    parserF.set_defaults(handle=finishDb)

    parserU = subparsers.add_parser('unfinishDb', help='fill data to database')
    parserU.add_argument('--loop', '-l', action='store_true')
    parserU.add_argument('--interval', '-itv', type=int, default=600, help='loop interval default(300) second')
    parserU.set_defaults(handle=unfinishDb)

    parserH = subparsers.add_parser('serve', help='serve that can watch or show')
    parserH.set_defaults(handle=serveDb)

    args = parser.parse_args(cmd)
    if not hasattr(args, 'handle'):
        parser.print_help()

    return args

def main(cmd=None):
    args = parse_args(cmd)
    if hasattr(args, 'handle'):
        args.handle(args) 

if __name__ == "__main__":
    main()