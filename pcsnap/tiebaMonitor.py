import time
import json
import re
import os

from sqlalchemy import Column, String, Integer, create_engine, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.schema import ForeignKey  # , relationship


Base = declarative_base()
DB = 'sqlite:///tieba_watcher.db'

class Tiezi(Base):
    __tablename__ = 'tiezi'

    id = Column(Integer, primary_key=True)
    link = Column(String(2048))
    title = Column(String(60))
    href = Column(String(258))
    author = Column(String(60))

    replyAuthor = Column(String(60))
    is_live = Column(Boolean, default=True)
    pointNum = Column(Integer, nullable=True)
    layerNum = Column(Integer, nullable=True)
    createTime = Column(String(60))
    replyDate = Column(String(60))
    updateDate = Column(String(60))

    def __repr__(self):
        return '<Exe %s %s>' % (self.id, self.title)


class Tieuser(Base):
    __tablename__ = 'tieuser'
    id = Column(Integer, primary_key=True)
    name = Column(String(2048))

    def __repr__(self):
        return '<Exe %s %s>' % (self.id, self.name)


def initDb(args):
    engine = create_engine(DB)
    Base.metadata.create_all(engine, checkfirst=True)
    return engine


def addProcessLog(DBSession, tasklist):
    session = DBSession()
    qAlv = session.query(Tiezi).filter_by(is_live=True)
    alvs = qAlv.all()
    for s in alvs:
        s.is_live = False
    print(len(alvs))
    # print(len(qAlv.all()))

    dt = int(time.time())
    for s in tasklist:
        tiezi = Tiezi(**s)
        tiezi.is_live = True
        session.add(tiezi)

    session.commit()


def watchDb(args):
    engine = create_engine(DB)
    DBSession = sessionmaker(bind=engine)
    while 1:
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
        tc = tb_crawl(args.url)
        addProcessLog(DBSession, tc)
        if not args.loop:
            break
        time.sleep(args.interval)


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
    headers = {"Accept-Language":"zh-CN,zh;q=0.9",
    "Cache-Control":"no-cache",
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Accept-Encoding":"gzip, deflate, br",
    "Host":"tieba.baidu.com",
    "Pragma":"no-cache",
    "Connection":"keep-alive",
    # "Referer":"https://www.baidu.com/",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.146 Safari/537.36"}
    response = requests.get(url, headers=headers)

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

    pat = re.compile(r'[0-9:\-]+')
    for ii, tie in enumerate(allTie):
        item = {}
        try:
            item['href'] = url
            item['layerNum'] = ii + 1
            item['title'] =  tie.xpath("./div/div[2]/div[1]/div[1]/a/@title")[0]
            item['link'] = 'http://tieba.baidu.com/' + tie.xpath("./div/div[2]/div[1]/div[1]/a/@href")[0]
            item['author'] = tie.xpath(".//div[@class='threadlist_author pull_right']//span[contains(@class,'tb_icon_author')]/@title")[0]
            item['pointNum'] = tie.xpath(".//div[@class ='col2_left j_threadlist_li_left']/span[@class='threadlist_rep_num center_text']/text()")[0]
            item['replyAuthor'] = tie.xpath(".//div[@class='threadlist_author pull_right']//span[contains(@class,'tb_icon_author')]/@title")[1]
            item['createTime'] = tie.xpath(".//span[@class='pull-right is_show_create_time']/text()")[0]
            # item['replyDate'] = re.findall('2', s[0])tie.xpath(".//span[@class='threadlist_reply_date pull_right j_reply_data']/text()").re('[0-9:\-]+')[0]
            item['replyDate'] = pat.findall(tie.xpath(".//span[@class='threadlist_reply_date pull_right j_reply_data']/text()")[0])[0]
        except Exception as e:
            continue
        
        yield item


def parse_args(cmd=None):
    start_url = 'http://tieba.baidu.com/f?kw=python&ie=utf-8&pn=0'
    import argparse
    parser = argparse.ArgumentParser(prog='requests')
    subparsers = parser.add_subparsers(help='sub-command help')
    parserT = subparsers.add_parser('init', help='init database')
    parserT.set_defaults(handle=initDb)

    parserW = subparsers.add_parser('watch', help='fill data to database')
    parserW.add_argument('--loop', '-l', action='store_true')
    parserW.add_argument('--interval', '-itv', type=int, default=600, help='loop interval default(300) second')
    parserW.add_argument('--url', default=start_url)
    parserW.set_defaults(handle=watchDb)
    args  = parser.parse_args(cmd)
    return args


def main(cmd=None):
    args = parse_args(cmd)
    if hasattr(args, 'handle'):
        args.handle(args) 


if __name__ == "__main__":
    main()
