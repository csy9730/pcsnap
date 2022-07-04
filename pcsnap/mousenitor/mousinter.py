import time
import win32api

OFS = 200
SC = 3

MAGIC_HEAD = (213,213)
MAGIC_HEAD2 = (233,233)
MAGIC_TAIL = (242,242)
MAGIC_TAIL2 = (222,222)

SAMPLE_TIME = 0.03
SAMPLE_TIME2 = SAMPLE_TIME *0.99

def expectCh(ch, tg):
    # print(ch, tg)
    if ch == tg:
        return True
    else:
        return False

# 
def genMsgWrap(cnt):
    N = len(cnt)
    yield MAGIC_HEAD
    yield MAGIC_HEAD2

    n1 = N // 256
    n2 = N % 256
    yield [n1,n2]
    for s in cnt:
        # print(s)
        yield [s, s]
    yield MAGIC_TAIL
    yield MAGIC_TAIL2


# genMsgWrap
def receiveMsgWrap(msg):
    s = 0
    buf = []
    for ch in msg:
        print('r', ch, s)
        if s == 0:
            if expectCh(ch, MAGIC_HEAD):
                s = 1
            else:
                s = 0
        elif s == 1:
            if expectCh(ch, MAGIC_HEAD2):
                s = 2
            else:
                s = 0
        elif s == 2:
            n1, n2 = ch
            N = n1*256+n2
            j = 0
            s = 3
        elif s == 3:
            m, _ = ch
            j = j+1
            # print(m, chr(m))
            buf.append((m%256).to_bytes(1, 'big'))# chr
            if j >= N: 
                s = 4
        elif s == 4:
            if expectCh(ch, MAGIC_TAIL):
                s = 5
            else:
                s = 0
        elif s == 5:
            if expectCh(ch, MAGIC_TAIL2):
                s = 0
                return b''.join(buf)
            else:
                s = 0

# win32api.Cursor
def sendPosChar(s, s2=None):
    if s2 is None:
        s2 = s
    win32api.SetCursorPos((s*SC+OFS, s2*SC+OFS))
    

def rcvPosChar():
    ch = win32api.GetCursorPos()
    return ((ch[0]-OFS)//SC, (ch[1]-OFS)//SC)

def genrcvPosChar(MX=150):
    for i in range(MX):
        yield rcvPosChar()
        time.sleep(SAMPLE_TIME2)

def sendPosMsgWrap(cnt):
    msg = genMsgWrap(cnt)
    for m in msg:
        sendPosChar(*m)
        time.sleep(SAMPLE_TIME)


def diff_coding(xx):
    px = 9999
    lst = []
    for x in xx:
        if x >= px:
            px = x + 1
        else:
            px = x
        lst.append(px)
    return lst

def diff_decoding(xx):
    px = 9999
    lst = []
    for x in xx:
        if x > px:
            px = x - 1
        else:
            px = x
        lst.append(px)
    return lst

def diff_coding2(xx):
    pxy = 1e8
    # lst = []
    for xy in xx:
        x,y=xy
        if x*1e4 + y >= pxy:
            py = y + 1
        else:
            py = y
        pxy = x*1e4 + py
        yield x, py
        # lst.append((x, py))
    # return lst

def diff_decoding2(xx):
    pxy = 1e8
    # lst = []
    for xy in xx:
        x,y = xy
        if x*1e4 + y > pxy:
            py = y - 1
        else:
            py = y
        pxy = x*1e4 + py
        yield x, py
        # lst.append(())
    # return lst

def test_genMsgWrap():
    cnt = b"hello world"
    msg = genMsgWrap(cnt)
    cnt2 = receiveMsgWrap(msg)
    assert cnt == cnt2, print(cnt, cnt2)
    # print(cnt2)

def test_genMsgWrap2():
    cnt = b"hello world"
    msg = genMsgWrap(cnt)
    msg = diff_coding2(msg)

    msg2 = diff_decoding2(msg)
    cnt2 = receiveMsgWrap(msg2)
    
    assert cnt == cnt2, print(cnt, cnt2)
    # print(cnt2)

def test_sendPosChar():
    s = 256
    sendPosChar(s)
    s2 = rcvPosChar()
    assert s2[0] == s


def demo_sendMsgWrap():
    print("begin demo_sendMsgWrap")
    # with open(pfn,'rb') as fp:
    #     cnt = fp.read()
    cnt = b"hello world"
    # N = len(cnt)
    sendPosMsgWrap(cnt)

def demo_receiveMsgWrap():
    gcv = genrcvPosChar()
    msg = receiveMsgWrap(gcv)
    print(msg)


def demo_sendMsgWrap2():
    print("begin demo_sendMsgWrap")
    cnt = b"hello world"
    msg = genMsgWrap(cnt)
    msg2 = diff_coding2(msg)
    for m in msg2:
        sendPosChar(*m)
        time.sleep(SAMPLE_TIME)

def demo_receiveMsgWrap2():
    gcv = genrcvPosChar()
    dc = diff_decoding2(gcv)
    msg = receiveMsgWrap(dc)
    print(msg)

def demo_send_receive():
    demo_sendMsgWrap()
    # demo_receiveMsgWrap()

def demo_send_receive_thread():
    import threading
    t = threading.Thread(target=demo_sendMsgWrap2)
    t2 = threading.Thread(target=demo_receiveMsgWrap2)
    t2.start()
    time.sleep(0.5)
    t.start()

def demoHandle(args):
    test_genMsgWrap()
    test_genMsgWrap2()
    test_sendPosChar()
    demo_send_receive_thread()


def sendMsgHandle(args):
    if args.input:
        print(args.input)
        with open(args.input, 'rb') as fp:
            cnt = fp.read()
    else:
        cnt = args.message
        cnt = cnt.encode('utf8')
    # print(cnt)
    sendPosMsgWrap(cnt)

def receiveMsgWrapHandle(args):
    gcv = genrcvPosChar(args.maxtimes)
    msg = receiveMsgWrap(gcv)
    if not msg:
        return
    if args.output:
        with open(args.output, 'wb') as fp:
            fp.write(msg)
    else:
        print(msg)


def parse_args(cmds=None):
    import argparse
    parser = argparse.ArgumentParser(description="your script description")
    parser.add_argument('--verbose', '-v', action='store_true', help='verbose mode')
    subparsers = parser.add_subparsers()

    receive_parser = subparsers.add_parser('receive', help='receive message')
    receive_parser.add_argument('--output', '-o', help='output file')
    receive_parser.add_argument('--maxtimes', '-m', type=int, default=150, help='maxtimes') 
    receive_parser.set_defaults(handle=receiveMsgWrapHandle)

    send_parser = subparsers.add_parser('send', help='send message')
    send_parser.add_argument('--input', '-i', help='input file') 
    send_parser.add_argument('--message', '-m', help='message') 
    send_parser.set_defaults(handle=sendMsgHandle)

    demo_parser = subparsers.add_parser('demo', help='demo message')
    demo_parser.set_defaults(handle=demoHandle)

    args = parser.parse_args(cmds) 
    if not hasattr(args, 'handle'):
        parser.print_help()
        
    return args


def main(cmds=None):
    args = parse_args(cmds)
    if hasattr(args, 'handle'):
        tm = time.time()
        args.handle(args)
        print(time.time()-tm)



if __name__ == "__main__":

    cmds = ['receive', '-m1500']
    cmds = ['send', '-m', 'hello world']

    cmds = ['receive', '-m4500', '-otmp.py']
    # cmds = ['send', '-i', r'logs\2022\2\8\MousePos.py']
    cmds = ['send', '-i', r'logs\2022\2\8\1.py']

    # cmds = ["receive", "-m1500"]
    # cmds = ['demo']
    main(cmds)

