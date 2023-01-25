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
os.makedirs(os.path.expanduser('~/.pcsnap'), exist_ok=True)
logger = getLogger(__name__, log_file=os.path.expanduser('~/.pcsnap/browtory.log'))

def getChromePath(input:Optional[str]=None) -> str:
    """
    ~\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe
    ~\\AppData\\Local\\Google\\Chrome\\User Data\\Default
    ~\\AppData/Roaming/360se6/Application/360se.exe
    ~\\AppData/Roaming/360se6/UserData/Default

    C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe
    C:\\ProgramData\\360\\360Chrome\\Chrome\\Application\\360chrome.exe
    C:\\ProgramData\\360\\360Chrome\\Chrome\\User Data\\Default
    C:\\Program Files\\360se\\360Chrome\\Chrome\\Application\\360chrome.exe
    C:\\Program Files\\360se\\360Chrome\\Chrome\\User Data\\Default

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

def chromeOper(input:Optional[str]=None, output=None, dry_run=False, **kwargs):
    try:
        input = getChromePath(input)
    except (FileNotFoundError, NotADirectoryError) as e:
        logger.error(e)
        exit(-1)

    input2 = quote(input, safe='')
    if output is None:
        output_dir = os.path.join("chromeDefault", time.strftime("%Y%m%d_%H%M%S", time.localtime()))
    else:
        output_dir = os.path.dirname(output)

    if not os.path.exists(output_dir):
        logger.info("mkdir %s", output_dir)
        os.makedirs(output_dir)

    files = ['history', 'Bookmarks', 'Cookies', 'Preferences', 'Login Data']
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


def analyze(results):
    import matplotlib.pyplot as plt
    prompt = input("[.] Type <c> to print or <p> to plot\n[>] ")

    if prompt == "c":
        for site, count in sites_count_sorted.items():
            print(site, count)
    elif prompt == "p":
        plt.bar(range(len(results)), results.values(), align='edge')
        plt.xticks(rotation=45)
        plt.xticks(range(len(results)), results.keys())
        plt.show()
    else:
        print("[.] Uh?")
        quit()

def chromeShow(input:str=None, output=None, **kwargs):
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
        print(sites_count_sorted)
        analyze (sites_count_sorted)

def chromeserve(**kwargs):
    logger.info("todo")

def parse_args(cmds=None):
    import argparse
    parser = argparse.ArgumentParser(
        description="input with chrome and bak it to a folder")
    subparsers = parser.add_subparsers(help='sub-command help')
    parserH = subparsers.add_parser('pull', help='pull data to database')
    parserH.add_argument('--input', '-i', help='''add a path to search path, a path such as "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" ''')
    parserH.add_argument('--output', '-o', help='output file to the dir')
    parserH.add_argument('--dry-run', action='store_true', help='dry run')                    
    parserH.set_defaults(handle=chromeOper)

    parserV = subparsers.add_parser('show', help='serve database to user ')
    parserV.add_argument('--input', '-i')
    parserV.add_argument('--output', '-o')

    parserV.set_defaults(handle=chromeShow)

    parserS = subparsers.add_parser('serve', help='serve database to user ')
    parserS.set_defaults(handle=chromeserve)
    args = parser.parse_args(None)

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
