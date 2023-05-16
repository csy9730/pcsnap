import os
import sqlite3
import shutil
import time
from urllib.parse import quote
import operator
from collections import OrderedDict
import logging
from typing import List, Dict, Optional

DEFAULT_PATH = r"User Data\Default"

# todo 
# - [ ] add: register, program, env  search chrome exe path
# - [ ] add: pull by sftp
# - [ ] add: select viewer

def get_all_config_path() -> List[str]:
    return [os.path.join(os.getcwd(), '.pcsnap'), os.path.join(os.path.dirname(os.path.abspath(__file__)), '.pcsnap'), os.path.expanduser('~/.pcsnap'), '/etc/pcsnap']


def find_config_path():
    ff = get_all_config_path()
    for f in ff:
        if os.path.isdir(f):
            return f
    return ff[-2]


class MyConfigWrap:
    def __init__(self, pfn:str):
        import configparser
        self.conf = configparser.ConfigParser()
        self.conf.read(pfn)
        self.filename = pfn
    
    def generate_default(self, force=False):
        if self.conf.sections() and not force:
            return
        import pcsnap
        import platform
        dct = {
            "default": {
                "created_at": time.strftime('%Y-%m-%d %H:%M:%S'), 
                "author": os.getlogin(), 
                "agent": ' '.join(['pcsnap', 'browtory', pcsnap.__version__, 'python', platform.python_version(), platform.system(), platform.version(), platform.machine()]), 
                # "log_file": LOG_FILE, 
                # "database": DB,
                # "hostname": socket.gethostname(),
                "user_id": 0
            }
        }
        self.conf.read_dict(dct)   
        self.conf.write(open(self.filename, 'w'))

    def update(self, key, value):
        dct = {"default": {"updated_at": time.strftime('%Y-%m-%d %H:%M:%S'), key:value}}
        self.conf.read_dict(dct)   
        self.conf.write(open(self.filename, 'w'))

    def get(self, section, option, **kwargs):
        return self.conf.get(section, option, **kwargs)


pdir = find_config_path()
os.makedirs(pdir, exist_ok=True)
pfn = os.path.join(pdir, "browtory.ini")
conf = MyConfigWrap(pfn)
# DB = conf.get('default', 'database', fallback=1)
REPO = conf.get('default', 'repo', fallback=os.path.join(pdir, ''))
LOG_FILE = conf.get('default','log_file', fallback=os.path.join(pdir, 'browtory.log'))

def getLogger(name:str, level="INFO", disable=False, log_file="procWatcher.log"):
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

logger = getLogger(__name__, log_file=LOG_FILE)

def guessChromePath(input:Optional[str]=None) -> str:
    """
    input
        None
    ~\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe
    ~\\AppData\\Local\\Google\\Chrome\\User Data\\Default
    ~\\AppData/Roaming/360se6/Application/360se.exe
    ~\\AppData/Roaming/360se6/UserData/Default

    C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe
    C:\\ProgramData\\360\\360Chrome\\Chrome\\Application\\360chrome.exe
    C:\\ProgramData\\360\\360Chrome\\Chrome\\User Data\\Default
    C:\\Program Files\\360se\\360Chrome\\Chrome\\Application\\360chrome.exe
    C:\\Program Files\\360se\\360Chrome\\Chrome\\User Data\\Default

    return 
        C:\\Program Files\\360se\\360Chrome\\Chrome\\User Data\Default
    """
    if input is None:
        input = os.path.expanduser('~')+r"\AppData\Local\Google\Chrome\User Data\Default"
    input = os.path.normcase(input)   

    if not os.path.exists(input):
        logger.error("%s not found", input)
        raise NotADirectoryError

    f, f2 = os.path.split(input)
    # print(f, f2)
    if f2 == 'default':
        pass
    elif f.endswith("application") and f2 in ['chrome.exe', '360chrome.exe', '360se.exe']:
        input = input[:-11] + DEFAULT_PATH
    else:
        logger.error("%s not recognition" % input)
        raise FileNotFoundError
    if not os.path.exists(input):
        logger.error("not found" % input)
        raise FileNotFoundError
    return input

def chromeOper(input:Optional[str]=None, output=None, dry_run=False, verbose=False, **kwargs):
    try:
        input = guessChromePath(input)
    except (FileNotFoundError, NotADirectoryError) as e:
        logger.error(e)
        exit(-1)

    input2 = quote(input, safe='')
    if output is None:
        if REPO:
            REPO2 = REPO if os.path.isabs(REPO) else os.path.join(pdir, REPO) 
            output_dir = os.path.join(REPO2, time.strftime("%Y%m%d_%H%M%S", time.localtime()))
        else:
            output_dir = os.path.join("chromeDefault", time.strftime("%Y%m%d_%H%M%S", time.localtime()))
    else:
        output_dir = os.path.dirname(output)

    if not os.path.exists(output_dir):
        logger.info("mkdir %s", output_dir)
        os.makedirs(output_dir)

    files = ['history', 'Bookmarks', 'Cookies', 'Preferences', 'Login Data']
    if verbose:
        files += ["Top Sites", "Network Action Predictor", "Last Session", "Last Tabs", "Web Data", "Visited Links", "Favicons", "Extension Cookies", "Shortcuts", "Secure Preferences", "heavy_ad_intervention_opt_out.db", "Origin Bound Certs", "tab_referer_url", "QuotaManager", "TransportSecurity", "Network/Cookies"]
        os.makedirs(os.path.join(output_dir, 'network'), exist_ok=True)
    for f in files:
        history_db = os.path.join(input, f)
        output = os.path.join(output_dir, f)
        if not os.path.exists(history_db):
            logger.warning("%s not found" % history_db)
            continue
        if not dry_run:
            logger.info('mv %s %s' %(history_db, output))
            shutil.copy(history_db, output)
        else:
            logger.info('mv %s %s' %(history_db, output))

def fetchChromeHistory(history_db:str):
    # querying the db
    c = sqlite3.connect(history_db)
    cursor = c.cursor()
    select_statement = "SELECT urls.url, urls.visit_count FROM urls, visits WHERE urls.id = visits.url;"
    cursor.execute(select_statement)

    results = cursor.fetchall()  # tuple

    return results

def url_parse(url:str) -> str:
    try:
        parsed_url_components = url.split('//')
        sublevel_split = parsed_url_components[1].split('/', 1)
        domain = sublevel_split[0].replace("www.", "")
        return domain
    except IndexError:
        print("URL format error!")


def analyze(results:Dict[str, int], showFig=False):
    import matplotlib.pyplot as plt
    # prompt = input("[.] Type <c> to print or <p> to plot\n[>] ")

    if not showFig:
        for site, count in results.items():
            print(site, count)
    else:
        plt.bar(range(len(results)), results.values(), align='edge')
        plt.xticks(rotation=45)
        plt.xticks(range(len(results)), results.keys())
        plt.show()

def chromeShow(input:str=None, output=None, show_fig=False, **kwargs):
    if input is None:
        chm = guessChromePath(input)
        input = os.path.join(chm, 'history')
    results = fetchChromeHistory(input)
    logger.info(len(results))
    if output:
        import pandas as pd
        df = pd.DataFrame(results)
        df.to_csv(output)
    else:
        sites_count = {}  # dict makes iterations easier :D

        for url, count in results:
            url = url_parse(url)
            if url in sites_count:
                sites_count[url] += 1
            else:
                sites_count[url] = 1

        sites_count_sorted = OrderedDict(
            sorted(sites_count.items(), key=operator.itemgetter(1), reverse=True))
        # print(sites_count_sorted)
        analyze(sites_count_sorted, show_fig)

def chromeserve(**kwargs):
    logger.info("todo")

def chromeConfig(key, value, **kwargs):
    conf.generate_default()
    conf.update(key, value)
    logger.info("update config:%s=%s" %(key,value))

def chromeConfigList(**kwargs):
    for sec in conf.conf.sections():
        keys = conf.conf.options(sec)
        for k in keys:
            print(k, conf.conf.get(sec, k))

def chromeConfigDel(key, **kwargs):
    conf.generate_default()
    conf.conf.remove_option('default', key)
    conf.conf.write(open(conf.filename, 'w'))
    logger.info("del config:%s" %key)

def parse_args(cmds=None):
    import argparse
    parser = argparse.ArgumentParser(
        description="input with chrome and bak it to a folder")
    subparsers = parser.add_subparsers(help='sub-command help')
    parserH = subparsers.add_parser('pull', help='pull data to database')
    parserH.add_argument('--input', '-i', help='''add a path to search path, a path such as "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" ''')
    parserH.add_argument('--output', '-o', help='output file to the dir')
    parserH.add_argument('--dry-run', action='store_true', help='dry run')  
    parserH.add_argument('--verbose', '-v', action='store_true', help='verbose')                 
    parserH.set_defaults(handle=chromeOper)

    parserV = subparsers.add_parser('show', help='show database to user ')
    parserV.add_argument('--input', '-i', help='history db file path')
    parserV.add_argument('--output', '-o', help='save to csv file')
    parserV.add_argument('--show-fig', action='store_true', help='show figure')  

    parserV.set_defaults(handle=chromeShow)

    parserS = subparsers.add_parser('serve', help='serve database to user ')
    parserS.set_defaults(handle=chromeserve)

    parserC = subparsers.add_parser('config', help='edit config file')

    subparsersC = parserC.add_subparsers(help='edit browtory config file')
    parserCA = subparsersC.add_parser('add', help='add config data')
    parserCA.add_argument('key')
    parserCA.add_argument('value')
    parserCA.set_defaults(handle=chromeConfig)

    parserCL = subparsersC.add_parser('list', help='list config data')
    parserCL.set_defaults(handle=chromeConfigList)

    parserCD = subparsersC.add_parser('del', help='delete config data')
    parserCD.add_argument('key')
    parserCD.set_defaults(handle=chromeConfigDel)

    args = parser.parse_args(cmds)

    if not hasattr(args, 'handle'):
        parser.print_help()
    return args


def main(cmds=None):
    args = parse_args(cmds)
    if hasattr(args, 'handle'):
        args.handle(**vars(args))

if __name__ == '__main__':
    main()
    # dump /load or merge / export sqlite3 to csv,
