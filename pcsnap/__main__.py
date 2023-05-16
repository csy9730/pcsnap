import os
import sys
import subprocess

def parse_args(cmds=None):
    import argparse
    parser = argparse.ArgumentParser(description="your script description")
    parser.add_argument('--verbose', '-v', action='store_true', help='verbose mode')
    args = parser.parse_args(cmds) 
    return args

def main(cmds=None):
    args = parse_args(cmds)
    print("""browtory
    flactodol
    genMarkdown
    recorder
    proc.procWatcher
    gitWalker2
    """)

if __name__ == "__main__":
    main()
