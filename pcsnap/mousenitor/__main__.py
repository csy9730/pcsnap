
'''
Author: ChenShengyong
LastEditors: Chen Shengyong
Date: 2022-05-07 17:47:10
LastEditTime: 2022-05-07 17:47:11
Description: Modify here please
'''
MAGIC_HEAD = (263,273)
MAGIC_HEAD2 = (273,283)
MAGIC_TAIL = (297,287)
MAGIC_TAIL2 = (287,277)

SAMPLE_TIME = 0.01
SAMPLE_TIME2 = SAMPLE_TIME *0.99
SAMPLE_TIME3 = SAMPLE_TIME * 0.2

def genrcvPosChar(MX=150):
    bak = None
    for i in range(MX):
        ch = rcvPosChar()
        if ch != bak:
            yield ch
            bak = ch
        time.sleep(SAMPLE_TIME3)

def sendMsgHandle(args):
    if args.input:
        print(args.input)
        with open(args.input, 'rb') as fp:
            cnt = fp.read()
    else:
        cnt = args.message
        cnt = cnt.encode('utf8')
    cnt = cnt[0: args.size]
    if args.dry_run:
        print(cnt)
    else:
        # sendPosMsgWrap(msg)
        tic = time.time()
        msg = genMsgWrap(cnt)
        msg = diff_coding2(msg)
        for m in msg:
            sendPosChar(*m)
            time.sleep(SAMPLE_TIME)
        print(time.time()-tic, args.size)

def receiveMsgWrapHandle(args):
    gcv = genrcvPosChar(args.maxtimes)
    dc = diff_decoding2(gcv)
    msg = receiveMsgWrap(dc)
    if not msg:
        return
    if args.output:
        with open(args.output, 'wb') as fp:
            fp.write(msg)
    else:
        print(msg)
