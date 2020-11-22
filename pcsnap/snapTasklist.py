import os
import subprocess
from pcsnap.utils.utils import timeCount
import csv
import json
import pprint

EXCLUDE_DIRS = ['.idea', '.vscode', '__pycache__']


def path2gitrepo():
    cmd = ["wmic", "process", "get","name,CommandLine,ProcessId,ExecutablePath", "/format:csv"]
    ret = subprocess.run(cmd, stdout=subprocess.PIPE)
    # print(ret)
    if ret.returncode == 0:
        return parseRemote(ret.stdout)


def parseRemote(ss):
    from io import StringIO
    cnt = StringIO(ss.decode('gb2312'))
    fp = csv.reader(cnt, delimiter = ',')
    return fp


def parse_args(cmd=None):
    import argparse
    parser = argparse.ArgumentParser(prog='os.walk git repo')
    parser.add_argument('--output', '-o', help='output file')
    parser.add_argument('--verbose', '-v', action='store_true', help='verbose')

    args = parser.parse_args(cmd)
    return args


@timeCount
def main(cmd=None):
    args = parse_args(cmd)
    lst = path2gitrepo()
    if args.output:
        with open(args.output, 'w',encoding="utf-8", newline='\n') as csvFile:
            writer = csv.writer(csvFile,delimiter=',')
            # for s in lst:      
            writer.writerows(lst)
    else:
        pprint.pprint(list(lst))


if __name__ == "__main__":
    main()
