import time
import json
import re
import os
import datetime as dt

from sqlalchemy import Column, String, Integer, create_engine, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.schema import ForeignKey  # , relationship
from config import DB

Base = declarative_base()

BASE_URL = 'http://tieba.baidu.com'
TIEBA_KEYWORD_URL = 'http://tieba.baidu.com/f?kw=%s&ie=utf-8&pn=0'

"""
- 查询所有用户
- 查询所有帖子
- 查询所有回帖记录

- 每天新增发帖数
    - 每月新增发帖数
    - 每季度新增发帖数
    - 每年新增发帖数
- 每天新增回帖数 去除抽奖导致的极大值
    - 每月新增回帖数
    - 每季度新增回帖数
    - 每年新增回帖数
- 查询指定帖子的所有回帖记录
- 查询回帖记录最多的top帖子
    - 每月top贴
    - 精品判断
    - nlp分析
        - top帖子标题分析 词云
        - 情感分析

- 每天新增用户数
    - 月活跃用户数
    - 周活跃用户数
- 查询指定用户的所有回帖
- 查询发帖记录最多的top用户
    - 每天
    - 每月
- 查询回帖记录最多的top用户
    - 每天
    - 每月
- 查询发帖回复累计最多的top用户
    - 每周
    - 每月
- 查询指定用户的所有发帖


"""

class Tieuser(Base):
    __tablename__ = 'tieuser'
    id = Column(Integer, primary_key=True)
    name = Column(String(2048))
    link = Column(String(512))
    tiezis = relationship("Tiezi", backref='author', lazy='dynamic')
    reply_logs = relationship("Tiezilog", backref='replyer', lazy='dynamic')

    def __repr__(self):
        return '<Exe %s %s>' % (self.id, self.name)


class Tiezi(Base):
    __tablename__ = 'tiezi'

    id = Column(Integer, primary_key=True)
    link = Column(String(2048))
    title = Column(String(600))
    # author = Column(String(160))
    content = Column(String(2120), nullable=True)
    createTime = Column(String(60), nullable=True)
    logs = relationship("Tiezilog", backref='tie', lazy='dynamic')
    author_id = Column(Integer, ForeignKey("tieuser.id"))

    def __repr__(self):
        return '<tiezi %s %s>' % (self.id, self.title)


class Tiezilog(Base):
    __tablename__ = 'tiezilog'
    id = Column(Integer, primary_key=True)

    # replyAuthor = Column(String(60))
    is_live = Column(Boolean, default=True)
    referer = Column(String(258))
    layerNum = Column(Integer, nullable=True)
    pointNum = Column(Integer, nullable=True)
    replyDate = Column(String(60), nullable=True)
    updateDate = Column(Integer, nullable=True)

    tiezi_id = Column(Integer, ForeignKey("tiezi.id"))
    replyer_id = Column(Integer, ForeignKey("tieuser.id"))

    def __repr__(self):
        return '<Tiezilog %s %s>' % (self.id, self.tie.title)


def initDb(args):
    engine = create_engine(DB)
    Base.metadata.create_all(engine) # , checkfirst=True
    return engine

def process_data(dat):
    for d in dat:
        d["createTime"] = process_datetime(d["createTime"])
        d["replyDate"] = process_datetime(d["replyDate"])
        # print(d["createTime"], d["replyDate"])
        # print(d.pop("author_link"), d.pop("replyer_link"))
        yield d

def process_datetime(tm, nowt=None):
    if nowt is None:
        nowt = dt.datetime.now()
    
    if ":" in tm and "-" in tm:
        adt = nowt
    elif ":" in tm and "-" not in tm:
        atm = dt.datetime.strptime(tm, "%H:%M") # 11:28 
        adt = dt.datetime(year=nowt.year, month=nowt.month, day=nowt.day, hour=atm.hour, minute=atm.minute, second=0, microsecond=0)
    elif ":" not in tm and "-"  in tm:
        # tm = '2020-12' # '2020-12-1'
        fd = re.findall(r'(\d+)-(\d+)-*(\d+)*', tm)[0]
        if len(fd[0]) > 2:
            adt = dt.datetime(year=int(fd[0]), month=int(fd[1]), day=int(fd[2] or 1))
        else:
            adt = dt.datetime(year=nowt.year, month=int(fd[0]), day=int(fd[1] or 1))
    else:
        adt = nowt
    return adt
    # re.findall(r'(\d+)-(\d+)-*(\d+)*', '2020-12')
    # re.findall(r'(\d2+)-(\d+)-*(\d+)*', '2020-12-1')
    # re.findall(r'((\d3+)-)(\d+)-*(\d+)*', '1-1')


def addProcessLog(DBSession, tasklist):
    session = DBSession()
    qAlv = session.query(Tiezilog).filter_by(is_live=True)
    alvs = qAlv.all()
    for s in alvs:
        s.is_live = False
    # print(len(alvs))

    nowt = int(time.time())

    for i,s in enumerate(tasklist):
        author = session.query(Tieuser).filter_by(link=s["author_link"]).first()
        if not author:
            s5 = {"name":s["author"], "link":s["author_link"]}
            author = Tieuser(**s5)
            session.add(author)
    
        replyer = session.query(Tieuser).filter_by(link=s["replyer_link"]).first()
        if s["replyer_link"] and not replyer:
            s6 = {"name": s["replyer"], "link": s["replyer_link"]}
            replyer = Tieuser(**s6)
            session.add(replyer) 

        tiezi = session.query(Tiezi).filter_by(link=s["link"]).first()
        if not tiezi:
            s2 = {k:v for k,v in s.items() if k in ["link", "title", "content", "createTime"]} 
            
            tiezi = Tiezi(**s2)
            tiezi.author_id = author.id
            session.add(tiezi)

        s3 = {k:v for k,v in s.items() if k in ["layerNum", "referer", "pointNum", "updateDate", "replyDate"]}
        pl = Tiezilog(updateDate=nowt, **s3)
        pl.is_live = True
        if replyer:
            pl.replyer_id = replyer.id

        tiezi.logs.append(pl)
        tiezi.author_id = author.id
        session.add(tiezi)

        session.add(pl)
    print("sum", i)
    session.commit()


def watchDb(args):
    engine = create_engine(DB)
    DBSession = sessionmaker(bind=engine)

    urls = [TIEBA_KEYWORD_URL % kw for kw in args.keyword] + [args.url]
    print(urls)
    while 1:
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        N = len(urls)
        # return 
        for url in urls:
            tc = tb_crawl(url)
            prd = process_data(tc)
            addProcessLog(DBSession, prd)
            time.sleep(args.interval/N)
        if not args.loop:
            return

def showDb(**kwargs):
    pass

def serveDb(**kwargs):
    pass

def getFirst(x):
    if isinstance(x, list):
        if x:
            return x[0]
        else:
            return None


def removeEmoji0(x):
    # highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    highpoints = re.compile(u'[\U00010000-\U0010ffff]')
    x2 = highpoints.sub(u'', x)
    return x2


def removeEmoji(x):
    import emoji
    x = removeEmoji0(emoji.demojize(x))
    return re.compile('[\\x00-\\x08\\x0b-\\x0c\\x0e-\\x1f]').sub(' ', x)


def tb_crawl(url):
    import requests
    from lxml import etree

    """
    sec-ch-ua: "Chromium";v="88", "Google Chrome";v="88", ";Not A Brand";v="99"
    sec-ch-ua-mobile: ?0
    Sec-Fetch-Dest: document
    Sec-Fetch-Mode: navigate
    Sec-Fetch-Site: none
    Sec-Fetch-User: ?1
    Upgrade-Insecure-Requests: 1
    """
    headers = {
        "Accept-Language":"zh-CN,zh;q=0.9",
        "Cache-Control":"no-cache",
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Encoding":"gzip, deflate, br",
        "Host":"tieba.baidu.com",
        "Pragma":"no-cache",
        "Connection":"keep-alive",
        # "Referer":"https://www.baidu.com/",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36"
    }
    response = requests.get(url, headers=headers)

    with  open('page_bak.html', 'w', encoding='utf-8') as fw:  
        fw.write(response.text)

    # doc = response.text
    # sector=etree.HTML(doc)
    if response.status_code != 200:
        print(response.status_code)
        exit(1)

    try:
        response_txt = str(response.content, 'utf-8')
    except Exception as e:
        response_txt = str(response.content, 'gbk')
    # response_txt = str(response.content,'utf-8')
    bs64_str = re.findall('<code class="pagelet_html" id="pagelet_html_frs-list/pagelet/thread_list" style="display:none;">[.\n\S\s]*?</code>', response_txt)
    
    bs64_str = ''.join(bs64_str).replace('<code class="pagelet_html" id="pagelet_html_frs-list/pagelet/thread_list" style="display:none;"><!--','')
    bs64_str = bs64_str.replace('--></code>','')
    # print(bs64_str)
    sector = etree.HTML(bs64_str)

    # allTie = sector.xpath("//ul[@id='thread_list']/li[@class='j_thread_list clearfix']")
    # $x('//ul[@id="thread_list"]')
    allTie = sector.xpath("//ul[@id='thread_list']//li[@class=' j_thread_list clearfix thread_item_box']")
    allTie.reverse()

    pat = re.compile(r'[0-9:\-]+')
    for ii, tie in enumerate(allTie):
        item = {}
        try:
            item['referer'] = url
            item['layerNum'] = ii + 1

            # import base64
            # author = tie.xpath(".//div[@class='threadlist_author pull_right']//span[contains(@class,'tb_icon_author')]/@title")[0].lstrip("主题作者: ")
            # bAuthor = base64.b64encode(str(author).encode('utf-8'))
            # author2 = tie.xpath(".//div[@class='threadlist_author pull_right']//span[contains(@class,'tb_icon_author')]/@title")[1].lstrip("最后回复人: ")
            # bAuthor2 = base64.b64encode(str(author2).encode('utf-8'))
            # item['author'] = author # removeEmoji(tie.xpath(".//div[@class='threadlist_author pull_right']//span[contains(@class,'tb_icon_author')]/@title")[0])
            # item['replyAuthor'] = author2 # removeEmoji(tie.xpath(".//div[@class='threadlist_author pull_right']//span[contains(@class,'tb_icon_author')]/@title")[1])

            # print([author, author2])
            item['title'] =  removeEmoji(tie.xpath("./div/div[2]/div[1]/div[1]/a/@title")[0])
            item['link'] = BASE_URL + tie.xpath("./div/div[2]/div[1]/div[1]/a/@href")[0]

            item['pointNum'] = tie.xpath(".//div[@class ='col2_left j_threadlist_li_left']/span[@class='threadlist_rep_num center_text']/text()")[0]

            # item['createTime'] = tie.xpath(".//span[@class='createtimecsss'/text()")[0]
            item['createTime'] = tie.xpath(".//span[@class='pull-right is_show_create_time']/text()")[0]
            # item['replyDate'] = tie.xpath(".//span[@class='threadlist_reply_date pull_right j_reply_data']/text()").re('[0-9:\-]+')[0]
            item['replyDate'] = pat.findall(tie.xpath(".//span[@class='threadlist_reply_date pull_right j_reply_data']/text()")[0])[0]
            item['content'] = removeEmoji(tie.xpath(".//div[@class='threadlist_text pull_left']/div/text()")[0])

            item['author_link'] = BASE_URL + tie.xpath('.//span[@class="frs-author-name-wrap"]/a[contains(@class,"frs-author-name")]/@href')[0]
            item['author'] = tie.xpath('.//span[@class="frs-author-name-wrap"]/a[contains(@class,"frs-author-name")]/text()')[0]
            item['replyer_link'] = BASE_URL + tie.xpath('.//span[contains(@class, "j_replyer")]/a[contains(@class,"frs-author-name")]/@href')[0]
            item['replyer'] = tie.xpath('.//span[contains(@class, "j_replyer")]/a[contains(@class,"frs-author-name")]/text()')[0]            

        except Exception as e:
            print(e)
            continue

        yield item


def parse_args(cmd=None):
    start_url = TIEBA_KEYWORD_URL % "kpl"
    import argparse
    parser = argparse.ArgumentParser(prog='requests')
    subparsers = parser.add_subparsers(help='sub-command help')
    parserT = subparsers.add_parser('init', help='init database')
    parserT.set_defaults(handle=initDb)

    parserW = subparsers.add_parser('watch', help='fill data to database')
    parserW.add_argument('--loop', '-l', action='store_true', help='enable loop watch')
    parserW.add_argument('--interval', '-itv', type=int, default=600, help='loop interval default(300) second')
    parserW.add_argument('--url', default=start_url)
    parserW.add_argument('--keyword', '-kw', action='append', default=[])
    parserW.set_defaults(handle=watchDb)

    parserS = subparsers.add_parser('show', help='show data to database')
    parserS.set_defaults(handle=showDb)

    parserH = subparsers.add_parser('serve', help='start server that can watch or show')
    parserH.add_argument('--port', default=5050)
    parserH.add_argument('--bind', default='0.0.0.0')
    parserH.set_defaults(handle=serveDb)
    args  = parser.parse_args(cmd)
    if not hasattr(args, 'handle'):
        parser.print_help()
    return args


def main(cmd=None):
    args = parse_args(cmd)
    if hasattr(args, 'handle'):
        args.handle(args) 


if __name__ == "__main__":
    main()
