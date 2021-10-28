import os
import sqlite3
import shutil
import time
import operator
from collections import OrderedDict

DEFAULT_PATH = r"User Data\Default"


def parse(url):
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


def fetchChromeHistory(history_db):
    # querying the db
    c = sqlite3.connect(history_db)
    cursor = c.cursor()
    select_statement = "SELECT urls.url, urls.visit_count FROM urls, visits WHERE urls.id = visits.url;"
    cursor.execute(select_statement)

    results = cursor.fetchall()  # tuple

    return results


def tmp(history_db=None):  
    import pandas as pd
    df = pd.DataFrame(results)
    df.to_csv("chrome_history.csv")

    sites_count = {}  # dict makes iterations easier :D

    for url, count in results:
        url = parse(url)
        if url in sites_count:
            sites_count[url] += 1
        else:
            sites_count[url] = 1

    sites_count_sorted = OrderedDict(
        sorted(sites_count.items(), key=operator.itemgetter(1), reverse=True))
    # print(sites_count_sorted)
    # analyze (sites_count_sorted)


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
        input = os.path.expanduser(
            '~')+r"\AppData\Local\Google\Chrome\User Data\Default"
    input = os.path.normcase(input)    
    if not os.path.exists(input):
        print(input, "not found")
        raise NotADirectoryError
    if input.endswith(r"application\360chrome.exe"):
        input = input[:-25]+DEFAULT_PATH
    if input.endswith(r"application\chrome.exe"):
        input = input[:-22]+DEFAULT_PATH
    if input.endswith(r"application\360se.exe"):
        input = input[:-21]+DEFAULT_PATH
    if not os.path.exists(input):
        print(input, "not found")
        raise FileNotFoundError
    
    return input

def chromeOper(input=None, output=None, fo=None, **kwargs):
    input = getChromePath(input)

    if output is None:        
        output = "./chromeDefault_" + \
            time.strftime("%Y%m%d_%H%M%S", time.localtime())

    if not os.path.exists(output):
        os.mkdir(output)

    history_db = os.path.join(input, 'history')
    results = fetchChromeHistory(history_db)
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


def parse_args():
    import argparse
    parser = argparse.ArgumentParser(
        description="input with chrome and bak it to a folder")
    parser.add_argument('--input', '-i', action='store', dest='input', help='''add a path to search path,
                                                                            a path such as "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" ''')
    parser.add_argument('--output', '-o', action='store',
                        dest='output', help='output bat file in the dir')
    parser.add_argument('--outputformat', '-fo', action='store',
                        dest='fo', help='output file format (csv or sqlite3)')
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    chromeOper(**vars(args))


if __name__ == '__main__':
    main()
    # dump /load or merge / export sqlite3 to csv,
