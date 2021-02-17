# -*- coding: utf-8 -*-

import json
from flask import render_template, session, redirect, url_for, current_app
from flask import request, Response, flash
from myapp import app
from models import Tiezi


# 定义路由
# 路由对应的函数处理
@app.route('/', methods=['GET', 'POST'])
def index():
    return "hello"


@app.route('/tiezi', methods=['GET', 'POST'])
def tiezi():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 30))
    p = Tiezi.query.paginate(page, per_page=per_page)
    tzs = p.items
    print(tzs)
    for tz in tzs:
        print(tz.logs[-1])
        tz.author2 = base64toUtf8(tz.author)
        tz.pointNum = tz.logs[-1].pointNum
    # Login.query.filter_by(user_id=current_user.id).order_by('id')
    return render_template("tiezi.html", paginate=p, tiezis=tzs)


def base64toUtf8(x):
    import base64
    # base64解码：传入Base64编码后的字节或字符，最后返回字节
    byt = base64.b64decode(x)
    x2 = byt.decode('utf-8')
    return x2


if __name__ == "__main__":
    app.run(port=5555)


"""
@main.route("/about/")
def about():
    form = LoginForm(request.form)
    return render_template("public/about.html", form=form)





@main.route('/index2', methods=['GET', 'POST'])
def index2():
    form = NameForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is None:
            user = User(username=form.name.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            if current_app.config['FLASKY_ADMIN']:
                send_email(current_app.config['FLASKY_ADMIN'],
                           'New User',
                           'mail/new_user',
                           user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data
        return redirect(url_for('.index'))
    return render_template('index.html',
                           form=form,
                           name=session.get('name'),
                           known=session.get('known', False))
"""                           