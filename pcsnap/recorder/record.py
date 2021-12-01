import os
import sys
import subprocess
import time
import json
from urllib.parse import quote
import logging


def setLogger(name, level="INFO", disable=False, log_file="record.log"):
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


_BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
statefile = os.path.join(_BASE, "recorder.jsonline")
logfile = os.path.join(_BASE, "recorder.log")
logger = setLogger(__name__, level="DEBUG", log_file=logfile)
"""
需求：
- [x] 实现history功能，包括 cmds，datetime
- [x] 实现记录单行命令行功能，包括 cmds，stdout，datetime
- [x] 额外记录：cwd，pid, 当前shell。
- [ ] 额外记录：环境变量
- [ ] 额外记录：程序返回码
- 实现tty功能，开启之后，记录所有命令行功能
    - 使用命令行无法实现该功能。
- 支持命令行携带重定向命令。
    - 使用命令行无法实现该功能。
- 支持 && || 的单行多命令语句
    - 使用命令行无法实现该功能 subprocess.run()。
    - 考虑使用命令字实现 os.system()。
    - 放弃该功能，使用bash脚本封装 && || 等功能
- [x] 支持jinja 的模板功能
    - [x] 支持 {{default}}
- [ ] 支持jsonline文件路径配置
- [ ] 支持config文件配置, ~/.recorder

设计：
- stdout ，可以使用: 重定向实现，使用subprocess.stdout.

实现：
"""

def cmds2quote2log(cmds):
    if isinstance(cmds, list):
        cmds = ' '.join(cmds)
    if cmds.endswith('.'):
        cmds += ' '
    p = quote(cmds, safe='')
    tm = time.strftime("%Y%m%d_%H%M%S", time.localtime()) 
    return p, tm


def genCmdline(cmds:str, dct={}):
    import jinja2
    tmpl = jinja2.Template(cmds)
    return tmpl.render(**dct)


def runCmds(args, cmds):
    exe = cmds[0]
    tm = time.localtime()
    logger.info(tm)
    _snap = time.strftime("%Y/%m/%d_%H:%M:%S", tm)
    _tm = time.strftime("%Y%m%d_%H%M%S", tm)
    _tm2 = str(time.time())
    logger.info(cmds)
    if isinstance(cmds, list):
        cmds = ' '.join(cmds)
    
    _default = os.path.join(_BASE, _tm2)
    params = {"datetime": _tm,"BASE": _BASE, "default": _default}

    if "{{default}}" in cmds:
        os.makedirs(_default, exist_ok=True)

    cmds = genCmdline(cmds, params)
    if cmds.endswith('.'):
        cmds += ' '
    p = os.path.join(_BASE, quote(cmds, safe=''))
    os.makedirs(p, exist_ok=True)
    flog = os.path.join(p, '%s.log' %(_tm))
    logger.info(cmds)

    with open(flog, 'a+') as fp:
        pp = subprocess.Popen(cmds, shell=True, stdout=fp, stderr=subprocess.STDOUT)

        params = {}
        outfile = None
        with open(statefile, 'a+') as fp:
            dct = dict(params=params, cmdline=cmds, shell=True, cwd=os.getcwd(), outfile=outfile, pid=pp.pid, 
            datatime=_snap)
            fp.write(json.dumps(dct)+'\n')

        pp.wait()

def parse_args(cmds=None):
    import argparse
    parser = argparse.ArgumentParser(description="your script description")
    parser.add_argument('--verbose', '-v', action='store_true', help='verbose mode')
    # parser.add_argument('--config', '-c', help='config mode')
    args,cmds2 = parser.parse_known_args(cmds) 
    return args,cmds2

def main(cmds=None):
    args,cmds2 = parse_args(cmds)
    logger.info(cmds)
    logger.info(args)
    if cmds2:
        runCmds(args, cmds2)

if __name__ == "__main__":
    main()
