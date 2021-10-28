import os
import sqlite3
import shutil
import time
import operator
from collections import OrderedDict


def fetchChromeHistory(history_db):
    # querying the db
    c = sqlite3.connect(history_db)
    cursor = c.cursor()
    select_statement = "SELECT urls.url, urls.visit_count FROM urls, visits WHERE urls.id = visits.url;"
    cursor.execute(select_statement)

    results = cursor.fetchall()  # tuple

    return results


def getChromePath(input):
    """
    C:\\Users\\admin\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe
    C:\\Users\\admin\\AppData\\Local\\Google\\Chrome\\User Data\\Default

    C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe

    C:\\ProgramData\\360\\360Chrome\\Chrome\\Application\\360chrome.exe
    C:\\ProgramData\\360\\360Chrome\\Chrome\\User Data\\Default

    C:\\Program Files\\360se\\360Chrome\\Chrome\\Application\\360chrome.exe
    C:\\Program Files\\360se\\360Chrome\\Chrome\\User Data\\Default

    C:\\ProgramData\\360\\360Chrome\\Chrome\\Application\\360chrome.exe
    C:\\ProgramData\\360\\360Chrome\\Chrome\\User Data\\Default

    C:\\Users\\admin\\AppData/Roaming/360se6/Application/360se.exe
    C:\\Users\\admin\\AppData/Roaming/360se6/UserData/Default

    """
    if input is None:
        input = os.path.expanduser('~') +\
        r"\AppData\Local\Google\Chrome\User Data\Default"
    input = os.path.normcase(input)    
    if not os.path.exists(input):
        print(input, "not found")
        raise NotADirectoryError

    DEFAULT_PATH = r"User Data\Default"
    if input.endswith(r"application\360chrome.exe"):
        input = input[:-25]+DEFAULT_PATH
    if input.endswith(r"application\chrome.exe"):
        input = input[:-22]+DEFAULT_PATH
    if input.endswith(r"application\360se.exe"):
        input = input[:-21]+DEFAULT_PATH

    if os.path.isdir(input):
        input = os.path.join(input, 'history')
        if not os.path.exists(input):
            print(input, "not found")
            raise FileNotFoundError

    return input


def chromeOper(input, output=None, fo=None, **kwargs):
    if output is None:        
        output = "./chromeDefault_" + \
            time.strftime("%Y%m%d_%H%M%S", time.localtime())

    if not os.path.exists(output):
        os.mkdir(output)

    results = fetchChromeHistory(input)
    import pprint
    pprint.pprint(results)

    return
    lst = [{
        "filename": "history",
        "rootdir": input,
        "format": "sqlite3",
        "description": "sqlite3"
    }, {
        "filename": "Bookmarks",
        "rootdir": input,
        "format": "json",
        "description": "json"
    }, {
        "filename": "Cookies",
        "rootdir": input,
        "format": "sqlite3",
        "description": "sqlite3"
    }, {
        "filename": "Login Data",
        "rootdir": input,
        "format": "sqlite3",
        "description": "sqlite3"
    }, {
        "filename": "Preferences",
        "rootdir": input,
        "format": "json",
        "description": "json"
    }, {
        "filename": "Favicons",
        "rootdir": input,
        "format": "sqlite3",
        "description": "sqlite3"
    }
    ]
    import json
    with open(os.path.join(output, "chromeHistory.file.json"), "w") as fp:
        json.dump(lst, fp, indent=4)

    for dct in lst:
        old_name = os.path.join(dct["rootdir"], dct["filename"])
        new_name = os.path.join(output, dct["filename"])
        shutil.copyfile(old_name, new_name)
    if fo == "csv" and lst[0]["format"] == "sqlite3":
        pass


def parse_args(cmds=None):
    import argparse
    parser = argparse.ArgumentParser(
        description="input with chrome and bak it to a folder")
    parser.add_argument('--input', '-i', help='''add a path to search path,\
                a path such as "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" ''')
    parser.add_argument('--output', '-o', action='store',
                        dest='output', help='output bat file in the dir')
    parser.add_argument('--outputformat', '-fo', action='store',
                        dest='fo', help='output file format (csv or sqlite3)')
    args = parser.parse_args(cmds)
    return args


def main(cmds=None):
    args = parse_args(cmds)

    args.input = getChromePath(args.input)
    print(args.input)
    chromeOper(**vars(args))


if __name__ == '__main__':
    # cmds = ['-i', r'D:\Projects\tmp\History']
    main()

