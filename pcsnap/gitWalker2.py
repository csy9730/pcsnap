import os
import sys
import os.path as osp
import asyncio
import json
from pcsnap.utils.utils import aTimeCount, timeCount
from typing import List, Dict, Generator, Any
from pathlib import PurePosixPath, Path

EXCLUDE_DIRS = ['.idea', '.vscode', '__pycache__']
g_dry_run = False
GIT_WALKER = ".gitwalker.json"

"""
    todo
    
    * add: add init/ status
    * add: push /pull

    * add: filter 
    * add: search git bare repo, subtree/submodule
    * add: status, clone, pull, push
    * add: git status & git log 
    * add: normalize git path/ posix-path
    * add: async subprocess
    * add: remote path

"""
def walk_dir(adir:str, maxlevels=10, quiet=0, use_posix_path=False) -> Generator[str, None, None]:
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


async def path2gitrepo(pth:str) -> str:
    cmd = ["git", "-C", pth, "remote", "-v"]
    # ret.returncode==0:

    # Create the subprocess, redirect the standard output into a pipe
    create = asyncio.create_subprocess_exec(*cmd,
                                            stdout=asyncio.subprocess.PIPE)
    proc = await create
    # Read one line of output
    data = await proc.stdout.read()
    remote = parseRemote0(data)
    await proc.wait()
    return remote


async def getGitStatus(pth:str) -> str:
    cmd = ["git", "-C", pth, "status", "-s"]
    # ret.returncode==0:

    # Create the subprocess, redirect the standard output into a pipe
    create = asyncio.create_subprocess_exec(*cmd,
                                            stdout=asyncio.subprocess.PIPE)
    proc = await create
    data = await proc.stdout.read()
    remote = parseStatus(data)
    await proc.wait()
    if remote:
        print(pth, '\n', remote)
    return remote


async def getGitLog(pth:str) -> str:
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


def isGitRepo(pth:str) -> bool:
    if osp.exists(pth):
        lst = os.listdir()
        if ".git" in lst:
            return True


async def gitClone(pth:str, repo):
    if osp.exists(pth):
        lst = os.listdir()
        if lst:
            if ".git" in lst:
                return ""
            else:
                return ""
    if not repo:
        return

    if isinstance(repo, list):
        repo = repo[0]
    [f1, f2] = osp.split(pth)
    if not osp.exists(f1):
        os.makedirs(f1)
    cmd = ["git", "-C", f1, "clone", repo, f2]
    print(cmd)
    # ret.returncode==0:
    if g_dry_run:
        return

    # Create the subprocess, redirect the standard output into a pipe
    create = asyncio.create_subprocess_exec(*cmd,
                                            stdout=asyncio.subprocess.PIPE)
    proc = await create
    data = await proc.stdout.read()
    remote = parseStatus(data)
    await proc.wait()
    return remote


async def gitPull(pth:str, repo):
    if not osp.exists(pth):
        print(pth, "not a path")
        return
        raise NotADirectoryError
    cmd = ["git", "-C", pth, "pull"]
    print(cmd)
    # Create the subprocess, redirect the standard output into a pipe
    create = asyncio.create_subprocess_exec(*cmd,
                                            stdout=asyncio.subprocess.PIPE)
    proc = await create
    data = await proc.stdout.read()
    remote = parseStatus(data)
    await proc.wait()
    return remote



async def gitPush(pth:str, repo):
    if not osp.exists(pth):
        print(pth, "not a path")
        return
        raise NotADirectoryError
    cmd = ["git", "-C", pth, "push"]
    print(cmd)
    # Create the subprocess, redirect the standard output into a pipe
    create = asyncio.create_subprocess_exec(*cmd,
                                            stdout=asyncio.subprocess.PIPE)
    proc = await create
    data = await proc.stdout.read()
    remote = parseStatus(data)
    await proc.wait()
    return remote


def parseRemote0(ss:bytes) -> str:
    ssp = ss.split(b'\n')
    if ssp:
        for s in ssp:
            sp = s.split()
            if len(sp) > 1:
                return sp[1].decode('utf-8')


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


def parseLines(ss:bytes) -> List[str]:
    ssp = ss.split(b'\n')
    return [s.decode('utf-8')  for s in ssp if s]


def parseStatus(ss: bytes) -> str:
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
    parser_s.add_argument('--exclude', action="append", help='exclude str')
    parser_s.add_argument('--include', action="append", help='include str')

    parser_s.set_defaults(handle=gitwalker_status)

    parser_c = subparsers.add_parser('clone', help='a help')
    parser_c.add_argument('--submodule', help='submodule file')
    parser_c.add_argument('--dry-run', action="store_true", help='dry_run')
    parser_c.add_argument('--exclude', action="append", help='exclude str')
    parser_c.add_argument('--include', action="append", help='include str')
    parser_c.set_defaults(handle=gitwalker_clone)

    parser_l = subparsers.add_parser('pull', help='a help')
    parser_l.add_argument('--exclude', action="append", help='exclude str')
    parser_l.add_argument('--include', action="append", help='include str')
    parser_l.set_defaults(handle=gitwalker_pull)
    
    parser_h = subparsers.add_parser('push', help='a help')
    parser_h.add_argument('--exclude', action="append", help='exclude str')
    parser_h.add_argument('--include', action="append", help='include str')
    parser_h.set_defaults(handle=gitwalker_push)

    parser_n = subparsers.add_parser('init', help='a help')
    parser_n.add_argument('--maxlevels', '-ml', default=10, help='max levels')
    parser_n.add_argument('--dry-run', action="store_true", help='include str')
    parser_n.add_argument('--exclude', action="append", help='exclude str')
    parser_n.add_argument('--include', action="append", help='include str')
    parser_n.add_argument('--posix-path', action='store_true', help='max levels')
    parser_n.set_defaults(handle=gitwalker_init)

    args = parser.parse_args(cmd)

    if "verbose" in args:
        args.verbose = len(args.verbose)

    return args, parser


async def gitwalker_init(args):
    lst = walk_dir(args.target, maxlevels=args.maxlevels, use_posix_path=args.posix_path)
  
    async def _wrap(p):
        return {"path": p, "remote": await path2gitrepo(p)}
    ret = await asyncio.gather(*[_wrap(p) for p in lst])

        
    if args.dry_run:
        print(json.dumps(ret, indent=2, ensure_ascii=False))
    else:
        with open(GIT_WALKER, 'w', encoding='utf-8') as fp:
            json.dump(ret, fp, indent=2, ensure_ascii=False)


def _getFirst(arg):
    if isinstance(arg, list) or hasattr(arg, '__iter__'):
        for x in arg:
            return x
        return None
    else:
        return arg


async def gitwalker_status(args):
    if not osp.exists(GIT_WALKER):
        raise FileNotFoundError(GIT_WALKER)

    with open(GIT_WALKER, "r") as fp:
        dct = json.load(fp)

        def filterPath(pth):
            if args.include:
                for s in args.include:
                    if s in pth:
                        return True
                return False
            if args.exclude:
                for s in args.exclude:
                    if s in pth:
                        return False 
                return True
            return True

        if args.verbose:
            async def _wrap(d):
                p = d['path']                
                await getGitStatus(p)
                if d['remote']:
                    log = await getGitLog(p)
                    print(log)

            await asyncio.wait([_wrap(d) for d in dct if filterPath(d['path'])])
        else:
            await asyncio.wait([getGitStatus(d['path']) for d in dct if filterPath(d['path'])])


async def gitwalker_clone(args):
    def filterPath(pth):
        if args.include:
            for s in args.include:
                if s in pth:
                    return True
            return False
        if args.exclude:
            for s in args.exclude:
                if s in pth:
                    return False 
            return True
        return True


    gitw = GIT_WALKER
    if not os.path.exists(gitw):
        raise FileNotFoundError

    global g_dry_run
    g_dry_run = args.dry_run
    
    with open(gitw, "r") as fp:
        dct = json.load(fp)
        await asyncio.wait([gitClone(d["path"], d["remote"]) for d in dct if filterPath(d['path'])])


async def gitwalker_pull(args):
    def filterPath(pth):
        if args.include:
            for s in args.include:
                if s in pth:
                    return True
            return False
        if args.exclude:
            for s in args.exclude:
                if s in pth:
                    return False 
            return True
        return True

    gitw = GIT_WALKER
    if not os.path.exists(gitw):
        raise FileNotFoundError
    
    with open(gitw, "r") as fp:
        dct = json.load(fp)
        await asyncio.wait([gitPull(d["path"], d["remote"]) for d in dct if filterPath(d['remote'])])


async def gitwalker_push(args):
    def filterPath(pth):
        if args.include:
            for s in args.include:
                if s in pth:
                    return True
            return False
        if args.exclude:
            for s in args.exclude:
                if s in pth:
                    return False 
            return True
        return True

    gitw = GIT_WALKER
    if not os.path.exists(gitw):
        raise FileNotFoundError
    
    with open(gitw, "r") as fp:
        dct = json.load(fp)
        await asyncio.wait([gitPush(d["path"], d["remote"]) for d in dct if filterPath(d['remote'])])


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
