# -*- coding: utf-8 -*-

import json
from flask import render_template, session, redirect, url_for, current_app
from flask import request, Response, flash
from myapp import app, db
from models import Tiezi, Tiezilog
from sqlalchemy import func
from argparse import Namespace


# 定义路由
# 路由对应的函数处理
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html")


@app.route('/about')
def about():
    return render_template("about.html")

# jobs = [{"title": "tieba", "content":"content", "link": "/jobs/tieba", "createTime": "20210401"}]

@app.route('/jobs')
def jobs():
    jobs= [Namespace(title="tieba", content="content", link="/jobs/tieba", createTime="20210401")]
    return render_template("jobs.html", jobs=jobs)


@app.route('/jobs/tieba')
def jobs_tieba():
    start_url = 'http://tieba.baidu.com/f?kw=%s&ie=utf-8&pn=0' % "python"
    from tiebaMonitor import watchDb
    jobs= [Namespace(title="tieba", content="content", link="/jobs/tieba", createTime="20210401")]
    args = Namespace(url=start_url, loop=False, interval=600)
    watchDb(args)
    return render_template("jobs.html", jobs=jobs)


@app.route('/tiezi', methods=['GET', 'POST'])
def tiezi():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 30))
    p = Tiezi.query.paginate(page, per_page=per_page)
    tzs = p.items
    tzs.reverse()
    print(tzs)
    for tz in tzs:
        print(tz.logs[-1])
        try:
            tz.author2 = base64toUtf8(tz.author)
            tz.pointNum = tz.logs[-1].pointNum
        except Exception as e:
            print(e)
    # Login.query.filter_by(user_id=current_user.id).order_by('id')
    return render_template("tiezi.html", paginate=p, tiezis=tzs)


@app.route('/tiezi/top', methods=['GET', 'POST'])
def tiezi_top():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 30))
    # p = Tiezi.query.order_by('pointNum').paginate(page, per_page=per_page)
    p = db.session.query(func.max(Tiezilog.pointNum), Tiezilog).group_by(Tiezilog.tiezi_id).order_by(-Tiezilog.pointNum).paginate(page, per_page=per_page)
    tzs = p.items
    # tzs.reverse()
    print(tzs)
    tzs2 = []
    for pointNum, tlog in tzs:
        # print(tz.logs[-1])
        tz = tlog.tie
        try:
            tz.author2 = base64toUtf8(tz.author)
            tz.author4 = base64toUtf8(tlog.replyAuthor)
            tz.pointNum = pointNum
            tzs2.append(tz)
        except Exception as e:
            print(e)
    return render_template("tiezi_top.html", paginate=p, tiezis=tzs2)


def base64toUtf8(x):
    import base64
    # base64解码：传入Base64编码后的字节或字符，最后返回字节
    byt = base64.b64decode(x)
    x2 = byt.decode('utf-8')
    return x2


if __name__ == "__main__":
    app.run(port=5555)