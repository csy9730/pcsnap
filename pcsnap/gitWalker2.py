import os
import sys
import subprocess
import asyncio
from pcsnap.utils.utils import aTimeCount, timeCount


EXCLUDE_DIRS = ['.idea', '.vscode', '__pycache__']

"""
    todo: search git bare repo
    todo: normalize git path
"""
def walk_dir(adir, maxlevels=10, quiet=0):
    if quiet < 2 and isinstance(adir, os.PathLike):
        adir = os.fspath(adir)
    if not quiet:
        print('Listing {!r}...'.format(adir))

    def _walk_dir(adir, ddir=None, maxlevels=10, quiet=0):
        try:
            names = os.listdir(adir)
            names.sort()
        except OSError:
            if quiet < 2:
                print("Can't list {!r}".format(adir))
            names = [] # yield return
        if ".git" in names and os.path.isdir(os.path.join(adir, ".git")):
            yield adir
        else:
            for name in names:
                if name in EXCLUDE_DIRS:
                    continue
                fullname = os.path.join(adir, name)
                if ddir is not None:
                    dfile = os.path.join(ddir, name)
                else:
                    dfile = None
                if os.path.isdir(fullname) and (maxlevels > 0 and name != os.curdir and name != os.pardir
                        and not os.path.islink(fullname)):          
                    yield from _walk_dir(fullname,
                                            ddir=dfile,
                                            maxlevels=maxlevels - 1,
                                            quiet=quiet)

    yield from _walk_dir(adir, None, maxlevels=maxlevels, quiet=quiet)


async def path2gitrepo(pth):
    cmd = ["git", "-C", pth, "remote", "-v"]
    # ret.returncode==0:

    # Create the subprocess, redirect the standard output into a pipe
    create = asyncio.create_subprocess_exec(*cmd,
                                            stdout=asyncio.subprocess.PIPE)
    proc = await create
    # Read one line of output
    data = await proc.stdout.readline()
    sp = data.split()
    if len(sp) > 1:
        remote = sp[1].decode('utf-8')
    else:
        remote = None

    await proc.wait()
    return remote

async def wrap(p):
    return {"path": p, "remote": await path2gitrepo(p)}

def parse_args(cmd=None):
    import argparse
    parser = argparse.ArgumentParser(prog='os.walk git repo')
    parser.add_argument('target', help='target path')
    parser.add_argument('--output', '-o', help='output file')
    parser.add_argument('--verbose', '-v', action='store_true', help='verbose')
    parser.add_argument('--maxlevels', '-ml', default=10, help='max levels')
    
    args = parser.parse_args(cmd)
    return args

@aTimeCount
async def main(cmd=None):
    args = parse_args(cmd)
    lst = walk_dir(args.target, maxlevels=args.maxlevels)
    # print(list(lst))
    # return
    if args.verbose:
        # ret = [{"path": p, "remote": await path2gitrepo(p)} for p in lst]        
        ret = await asyncio.gather(*[wrap(p) for p in lst])
    else:
        ret = list(lst)

    if args.output:
        import json
        with open(args.output, 'w', encoding='utf-8') as fp:
            json.dump(ret, fp, indent=2, ensure_ascii=False)
    else:
        pass #print(ret)


if __name__ == "__main__":
    if sys.platform == "win32":
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()
    loop.run_until_complete(asyncio.gather(
        main(),
    ))
    loop.close()
