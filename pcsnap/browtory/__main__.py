import os
import sqlite3
import shutil
import time
from urllib.parse import quote

DEFAULT_PATH = r"User Data\Default"


def getChromePath(input):
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
        print(input, "not found")
        raise NotADirectoryError

    f, f2 = os.path.split(input)
    # print(f, f2)
    if f2 == 'default':
        pass
    elif f.endswith("application") and f2 in ['chrome.exe', '360chrome.exe', '360se.exe']:
        input = input[:-11] + DEFAULT_PATH
    else:
        print(input, "not recognition")
        raise FileNotFoundError
    if not os.path.exists(input):
        print(input, "not found")
        raise FileNotFoundError
    return input

def chromeOper(input=None, output=None, dry_run=None, **kwargs):
    try:
        input = getChromePath(input)
    except (FileNotFoundError, NotADirectoryError) as e:
        print(e)
        exit(-1)

    input2 = quote(input, safe='')
    if output is None:
        output_dir = os.path.join("chromeDefault", input2, time.strftime("%Y%m%d_%H%M%S", time.localtime()))
    else:
        output_dir = os.path.dirname(output)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    files = ['history', 'Bookmarks', 'Cookies']
    for f in files:
        history_db = os.path.join(input, f)
        output = os.path.join(output_dir, f)
        if not dry_run:
            shutil.copy(history_db, output)
        else:
            print('mv %s %s' %(history_db, output))

def parse_args(cmds=None):
    import argparse
    parser = argparse.ArgumentParser(
        description="input with chrome and bak it to a folder")
    subparsers = parser.add_subparsers(help='sub-command help')
    parserH = subparsers.add_parser('pull', help='pull data to database')
    parserH.add_argument('--input', '-i', action='store', dest='input', help='''add a path to search path,
                                                                            a path such as "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" ''')
    parserH.add_argument('--output', '-o', help='output bat file in the dir')
    parserH.add_argument('--dry-run', action='store_true', help='dry run')                    
    parserH.set_defaults(handle=chromeOper)
    args = parser.parse_args(None)
    return args


def main(cmds=None):
    args = parse_args(cmds)
    if hasattr(args, 'handle'):
        args.handle(**vars(args))
    # chromeOper(**vars(args))

if __name__ == '__main__':
    main()
    # dump /load or merge / export sqlite3 to csv,
