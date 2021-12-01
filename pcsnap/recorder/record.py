import os
import sys
import subprocess
import time
import json

logfile = "recorder.jsonline"

"""
需求：
- 实现history功能，包括 cmds，datetime
- 实现记录单行命令行功能，包括 cmds，stdout，datetime
- 额外记录：cwd，pid, 当前shell。
- 额外记录：环境变量
- 额外记录：程序返回码
- 实现tty功能，开启之后，记录所有命令行功能
    - 使用命令行无法实现该功能。
- 支持命令行携带重定向命令。
    - 使用命令行无法实现该功能。
- 支持 && || 的单行多命令语句
    - 使用命令行无法实现该功能 subprocess.run()。
    - 考虑使用命令字实现 os.system()。
    - 放弃该功能，使用bash脚本封装 && || 等功能

设计：
- stdout ，可以使用: 重定向实现，使用subprocess.stdout.

实现：
"""
def main(cmds=None):
    print(sys.argv)
    if len(sys.argv) == 1:
        print("record.py ")
    elif sys.argv[1] == '--help':
        print("record.py ")
    elif sys.argv[1] == '--version':
        print("record.py ")   
    else:
        cmds = sys.argv[1:]
        runCmds(cmds)

def runCmds(cmds):
    exe = cmds[0]
    # if exe in ['ls', 'dir']:
    #     return
    _snap = time.strftime("%Y/%m/%d_%H:%M:%S", time.localtime())
    pp = subprocess.Popen(cmds)
    params = {}
    outfile = None
    with open(logfile, 'a+') as fp:
        dct = dict(params=params, cmdline=cmds, shell=True, cwd=os.getcwd(), outfile=outfile, pid=pp.pid, 
        datatime=_snap)
        fp.write(json.dumps(dct)+'\n')
    pp.wait()

if __name__ == "__main__":
    main()
