'''
Author: Chen
LastEditors: Chen
Date: 2022-05-07 17:47:10
LastEditTime: 2022-05-07 17:47:11
Description: Modify here please
'''
MAGIC_HEAD = (263,273)
MAGIC_HEAD2 = (273,283)
MAGIC_TAIL = (297,287)
MAGIC_TAIL2 = (287,277)

SAMPLE_TIME = 0.01
SAMPLE_TIME2 = SAMPLE_TIME *0.99
SAMPLE_TIME3 = SAMPLE_TIME * 0.2

def genrcvPosChar(MX=150):
    bak = None
    for i in range(MX):
        ch = rcvPosChar()
        if ch != bak:
            yield ch
            bak = ch
        time.sleep(SAMPLE_TIME3)

def sendMsgHandle(args):
    if args.input:
        print(args.input)
        with open(args.input, 'rb') as fp:
            cnt = fp.read()
    else:
        cnt = args.message
        cnt = cnt.encode('utf8')
    cnt = cnt[0: args.size]
    if args.dry_run:
        print(cnt)
    else:
        # sendPosMsgWrap(msg)
        tic = time.time()
        msg = genMsgWrap(cnt)
        msg = diff_coding2(msg)
        for m in msg:
            sendPosChar(*m)
            time.sleep(SAMPLE_TIME)
        print(time.time()-tic, args.size)

def receiveMsgWrapHandle(args):
    gcv = genrcvPosChar(args.maxtimes)
    dc = diff_decoding2(gcv)
    msg = receiveMsgWrap(dc)
    if not msg:
        return
    if args.output:
        with open(args.output, 'wb') as fp:
            fp.write(msg)
    else:
        print(msg)



def gen_db_path(pth):
    DB = 'sqlite:///%s/tasklists.db' % pth
    DB = DB.replace('\\', '/')
    return DB


def get_all_config_path():
    return [os.path.join(os.getcwd(), '.pcsnap'), os.path.join(os.path.dirname(os.path.abspath(__file__)), '.pcsnap'), os.path.expanduser('~/.pcsnap'), '/etc/.pcsnap']
# print(get_all_config_dir())

def find_config_path():
    ff = get_all_config_path()
    for f in ff:
        if os.path.isdir(f):
            return f
    return ff[-2]

def new_get_conffile(pfn):
    _conf = configparser.ConfigParser()
    _conf.read(pfn)
    # print(_conf.sections())
    if not _conf.sections():
        DB = gen_db_path(os.path.expanduser('~/.pcsnap'))
        LOG_FILE = os.path.expanduser('~/.pcsnap/pcsnap.log')
        dct = {"default": {"created_at": time.strftime('%Y-%m-%d %H:%M:%S'), "author": "foo", "agent": "pcsnap.proc", "log_file": LOG_FILE, "database": DB}}
        _conf.read_dict(dct)   
        _conf.write(open(pfn, 'w'))
    else:
        dct = {"default": {"visited_at": time.strftime('%Y-%m-%d %H:%M:%S')}}
        _conf.read_dict(dct)   
        _conf.write(open(pfn, 'w'))
    return _conf


pth = os.path.expanduser('~/.pcsnap')
os.makedirs(pth, exist_ok=True)
pfn = os.path.join(find_config_path(), "procWatcher.ini")
conf = new_get_conffile(pfn)
DB = conf.get('default', 'database')
LOG_FILE = conf.get('default','log_file')
logger = getLogger(__name__, log_file=LOG_FILE)

		
