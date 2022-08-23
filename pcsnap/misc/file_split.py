import os
import sys
import shutil

import argparse

def parse_args(cmd=None):
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='sub-command help')
    parser_sp = subparsers.add_parser('split', help='split help')
    parser_sp.add_argument('--bytes', '-b', type=int, action='append', default=[])
    parser_sp.add_argument('--offset', '-of', type=int, default=0)
    parser_sp.add_argument('--file', '-f')
    parser_sp.add_argument('--output', '-o')
    parser_sp.add_argument('--block-size', '-bs', type=int, default=4096)
    parser_sp.add_argument('--verbose', '-v', action='store_true')
    parser_sp.set_defaults(handle=split_handle)

    parser_merge = subparsers.add_parser('merge', help='merge help, append multiple file content to output file')    
    parser_merge.add_argument('--file', '-f',  action='append')
    parser_merge.add_argument('--output', '-o')
    parser_merge.add_argument('--verbose', '-v', action='store_true')
    parser_merge.set_defaults(handle=merge_handle)
    args = parser.parse_args(cmd)
    if not hasattr(args, 'handle'):
        parser.print_help()
    return args

def split_handle(args):
    if not args.file: return
    with open(args.file, 'rb') as fp:
        fp.seek(args.offset, 1)
        for i, byt in enumerate(args.bytes):
            cnt = fp.read(byt)
            with open(args.output+'.%d'%(i+1), 'wb') as fw:
                if cnt:
                    fw.write(cnt)
        with open(args.output+'.%d'%(i+2), 'wb') as fw2:
            while True:
                file_eof = fp.read(args.block_size)
                if not file_eof:
                    print('End Of File', fp.tell())
                    break
                else:
                    fw2.write(file_eof)

def merge_handle(args):
    if not args.file: return
    import shutil

    if args.output is None:
        for f in args.file[1:]:
            if args.verbose:
                print(os.path.getsize(f), end='\t')
            shutil.copyfileobj(open(f, 'rb'), open(args.file[0], 'ab+'))
    else:
        for f in args.file:
            if args.verbose:
                print(os.path.getsize(f), end='\t')
            shutil.copyfileobj(open(f, 'rb'), open(args.output, 'ab+'))
    if args.verbose:
        print()

def merge_handle2(args):
    if not args.file: return
    command = 'cat %s > %s' % (' '.join(args.file), args.output)
    command2 = 'copy /b %s %s' % (' '.join(args.file), args.output)
    if args.verbose:
        print(command)
    os.system(command)

def main(cmd=None):
    args = parse_args(cmd)
    if hasattr(args, "handle"):
       args.handle(args)

if __name__ == "__main__":
    # cmd = ['split', '-f', 'file_split.py', '-o', 'a3.py', ]
    cmd = ['merge', '-f', 'a3.py.1',  '-f', 'a3.py.2','-o', 'a3merge.py', '-v']
    main()