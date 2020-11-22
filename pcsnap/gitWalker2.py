import os
import sys
import subprocess
import asyncio
import json
from pcsnap.utils.utils import aTimeCount, timeCount

from pathlib import PurePosixPath, Path

EXCLUDE_DIRS = ['.idea', '.vscode', '__pycache__']

"""
    todo
    
    * add: search git bare repo, subtree/submodule
    * add: status, clone, pull, push
    * add: git status & git log 
    * add: normalize git path/ posix-path
    * add: async subprocess
    * add: remote path

"""
def walk_dir(adir, maxlevels=10, quiet=0, use_posix_path=None):
    if quiet < 2 and isinstance(adir, os.PathLike):
        adir = os.fspath(adir)
    if not quiet:
        print('Listing {!r}...'.format(adir))

    def _walk_dir(adir, ddir=None, maxlevels=10):
        try:
            names = os.listdir(adir)
            names.sort()
        except OSError:
            if quiet < 2:
                print("Can't list {!r}".format(adir))
            names = [] # yield return
        if ".git" in names and os.path.isdir(os.path.join(adir, ".git")):
            if use_posix_path:
                adir = str(PurePosixPath(Path(adir)))
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
                                            maxlevels=maxlevels - 1)

    yield from _walk_dir(adir, None, maxlevels=maxlevels)


async def path2gitrepo(pth):
    cmd = ["git", "-C", pth, "remote", "-v"]
    # ret.returncode==0:

    # Create the subprocess, redirect the standard output into a pipe
    create = asyncio.create_subprocess_exec(*cmd,
                                            stdout=asyncio.subprocess.PIPE)
    proc = await create
    # Read one line of output
    data = await proc.stdout.read()
    remote = parseRemote(data)
    await proc.wait()
    return remote


async def getGitStatus(pth):
    cmd = ["git", "-C", pth, "status", "-s"]
    # ret.returncode==0:

    # Create the subprocess, redirect the standard output into a pipe
    create = asyncio.create_subprocess_exec(*cmd,
                                            stdout=asyncio.subprocess.PIPE)
    proc = await create
    data = await proc.stdout.read()
    remote = parseStatus(data)
    await proc.wait()
    return remote


async def getGitLog(pth):
    cmd = ["git", "-C", pth, "log", "master..origin/master", "-3", "--oneline", "-q"]
    # ret.returncode==0:

    # Create the subprocess, redirect the standard output into a pipe
    create = asyncio.create_subprocess_exec(*cmd,
                                            stdout=asyncio.subprocess.PIPE)
    proc = await create
    data = await proc.stdout.read()
    remote = parseStatus(data)
    await proc.wait()
    return remote


async def gitClone(pth, repo):
    # os.listdir()
    cmd = ["git", "-C", pth, "clone", repo, "."]
    # ret.returncode==0:

    # Create the subprocess, redirect the standard output into a pipe
    create = asyncio.create_subprocess_exec(*cmd,
                                            stdout=asyncio.subprocess.PIPE)
    proc = await create
    data = await proc.stdout.read()
    remote = parseStatus(data)
    await proc.wait()
    return remote

def parseRemote(ss):
    ssp = ss.split(b'\n')
    rm = set()
    if ssp:
        for s in ssp:
            sp = s.split()
            if len(sp) > 1:
                rm.add(sp[1].decode('utf-8'))
        return list(rm)
    else:
        return []


def parseLines(ss):
    ssp = ss.split(b'\n')
    return [s.decode('utf-8')  for s in ssp if s]


def parseStatus(ss):
    # ssp = ss.split(b'\n')
    return ss.decode('utf-8') # [s for s in ssp if s] 


def parse_args(cmd=None):
    import argparse
    parser = argparse.ArgumentParser(prog='os.walk git repo')
    parser.add_argument('-C', dest='target', default='.', help='output file')

    subparsers = parser.add_subparsers(help='sub-command help')#,action='store',dest = 'subFlag')
    parser_s = subparsers.add_parser('status', help='a help')

    parser_s.add_argument('--output', '-o', help='output file')
    # parser.add_argument('--verbose', '-v', action='store_true', help='verbose')
    parser_s.add_argument('--verbose', '-v', const=None, action='append_const', default=[], help='verbose')
    parser_s.add_argument('--maxlevels', '-ml', default=10, help='max levels')
    parser_s.add_argument('--posix-path', action='store_true', help='max levels')

    parser_s.set_defaults(handle=gitwalker_status)

    parser_s = subparsers.add_parser('clone', help='a help')
    parser_s.set_defaults(handle=gitwalker_clone)
    parser_s.add_argument('--submodule', help='submodule file')


    parser_s = subparsers.add_parser('pull', help='a help')
    parser_s.set_defaults(handle=gitwalker_pull)

    parser_s = subparsers.add_parser('push', help='a help')
    parser_s.set_defaults(handle=gitwalker_push)

    args = parser.parse_args(cmd)

    if "verbose" in args:
        args.verbose = len(args.verbose)

    return args, parser


async def gitwalker_status(args):
    lst = walk_dir(args.target, maxlevels=args.maxlevels, use_posix_path=args.posix_path)
    if args.verbose==0:
        ret = list(lst)
  
    elif args.verbose == 1:
        # ret = [{"path": p, "remote": await path2gitrepo(p)} for p in lst]   
        async def _wrap(p):
            return {"path": p, "remote": await path2gitrepo(p)}
        ret = await asyncio.gather(*[_wrap(p) for p in lst])
    else:
        async def _wrap2(p):
            return {"path": p, "remote": await path2gitrepo(p), "status": await getGitStatus(p), "remoteLog": await getGitLog(p)}
        ret = await asyncio.gather(*[_wrap2(p) for p in lst])
        

    if args.output:        
        with open(args.output, 'w', encoding='utf-8') as fp:
            json.dump(ret, fp, indent=2, ensure_ascii=False)
    else:
        print(json.dumps(ret, indent=2, ensure_ascii=False))


async def gitwalker_clone(args):
    args.submodule
    if not os.path.exists(args.submodule):
        raise FileNotFoundError
    with open(args.submodule, "r") as fp:
        dct = json.load(fp)
        for d in dct:
            ret = await asyncio.gather(*[gitClone(d["path"], d["remote"]) for d in dct])




async def gitwalker_pull(args):
    pass


async def gitwalker_push(args):
    pass


@aTimeCount
async def main(cmd=None):
    args, parser = parse_args(cmd)
    if "handle" in args:
        await args.handle(args)
    else:
        parser.print_help()


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
