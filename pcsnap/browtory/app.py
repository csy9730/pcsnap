import os
import datetime
import json
from flask import Flask, render_template, request
from flask_restful import reqparse, abort, Api, Resource
from flask_bootstrap import Bootstrap

from sqlalchemy import Column, String, Integer, create_engine, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.schema import ForeignKey  # , relationship
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)


basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@example.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'History_acer')

    @staticmethod
    def init_app(app):
        pass

app.config.from_object(Config)
api = Api(app)
db = SQLAlchemy()
db.init_app(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap()
bootstrap.init_app(app)


class Urls(db.Model):
    __tablename__ = 'urls'
    id = Column(Integer, primary_key=True)
    url = Column(String(260))
    title = Column(String(260))

    visit_count = db.Column(db.Integer, default=0)
    typed_count = db.Column(db.Integer, default=0)
    last_visit_time = db.Column(db.Integer, default=0)
    hidden = db.Column(Boolean, default=0)

    @property
    def _last_visit_time(self):
        return datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=self.last_visit_time)

    def __repr__(self):
        return '<Urls %s %s>' % (self.id, self.url)


class Visits(db.Model):
    __tablename__ = 'visits'
    id = Column(Integer, primary_key=True)
    url = db.Column(db.Integer, db.ForeignKey('urls.id'))
    visit_time = db.Column(db.Integer)
    from_visit = db.Column(db.Integer, db.ForeignKey('visits.id'))
    transition = db.Column(db.Integer)
    segment_id = db.Column(db.Integer)
    visit_duration = db.Column(db.Integer)

    publicly_routable = Column(Boolean, default=False)
    incremented_omnibox_typed_score = Column(Boolean, default=False)

    urls = relationship("Urls",backref="visits") 

    @property
    def _visit_time(self):
        return datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=self.visit_time)

    def __repr__(self):
        return '<Visits %s %s>' % (self.id, self.url)

    def to_dict(self):
        KEYS = ['id', "name", "body", "is_active"]
        return {k: v for k, v in self.__dict__.items() if k in KEYS}


class Downloads(db.Model):
    __tablename__ = 'downloads'
    id = Column(Integer, primary_key=True)
    guid = Column(String(40))
    current_path = Column(String(360))
    target_path = Column(String(360))
    referrer = Column(String(660))
    site_url = Column(String(660))
    tab_url = Column(String(660))
    tab_referrer_url = Column(String(660))

    last_modified = Column(String(60))
    etag = Column(String(90))

    mime_type = Column(String(50))
    original_mime_type = Column(String(50))

    start_time = db.Column(db.Integer, default=0)
    received_bytes = db.Column(db.Integer, default=0)
    total_bytes = db.Column(db.Integer, default=0)

    state = db.Column(db.Integer, default=0)
    danger_type = db.Column(db.Integer, default=0)

    interrupt_reason = db.Column(db.Integer, default=0)
    # hash = db.Column(db.Integer, default=0)
    # http_method
    # by_ext_name
    # by_ext_id
    end_time = db.Column(db.Integer, default=0)
    opened = db.Column(db.Boolean, default=0)

    last_access_time = db.Column(db.Integer, default=0)
    transient = db.Column(db.Boolean, default=False)


class Keyword_search_terms(db.Model):
    __tablename__ = 'keyword_search_terms'

    url_id = Column(Integer, primary_key=True)
    keyword_id = Column(Integer)
    term = Column(String(360))
    normalized_term = Column(String(360))


class Downloads_url_chains(db.Model):
    __tablename__ = 'downloads_url_chains'

    id = Column(Integer, primary_key=True)
    chain_index = Column(Integer)
    url = Column(String(360))


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/visits')
def todos_view():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    q = Visits.query# .order_by(Visits.id)
    p = q.paginate(page, per_page=per_page)
    return render_template("browser/visit_list.html",  paginate=p, todolist=p.items)


@app.route('/visits/recent')
def visits_recent_view():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    q = Visits.query.order_by(Visits.visit_time.desc())
    p = q.paginate(page, per_page=per_page)
    return render_template("browser/visit_list.html", todolist=p.items)


@app.route('/visits/<int:todo_id>')
def todo_view(todo_id):
    td = Visits.query.filter_by(id=todo_id).first()
    print(td.from_visit, "from_visit", td.from_visit>0)
    if td:
        return render_template("browser/visit_put.html", todo=td)
    else:
        abort(404, message="Todo {} doesn't exist".format(todo_id))


@app.route('/urls')
def urls_view():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    q = Urls.query# .order_by(Visits.id)
    p = q.paginate(page, per_page=per_page)
    return render_template("browser/url_list.html",  paginate=p, todolist=p.items)


@app.route('/urls/top')
def urls_top_view():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    q = Urls.query.order_by(Urls.visit_count.desc())
    p = q.paginate(page, per_page=per_page)
    return render_template("browser/url_list.html", todolist=p.items)


@app.route('/urls/recent')
def urls_recent_view():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    q = Urls.query.order_by(Urls.last_visit_time.desc())
    p = q.paginate(page, per_page=per_page)
    return render_template("browser/url_list.html", todolist=p.items)


@app.route('/urls/<int:todo_id>')
def url_view(todo_id):
    td = Urls.query.filter_by(id=todo_id).first()
    if td:
        visit_list = Visits.query.filter_by(url=todo_id).all()
        return render_template("browser/url_put.html", todo=td, visit_list=visit_list)
    else:
        abort(404, message="Todo {} doesn't exist".format(todo_id))


if __name__ == '__main__':
    # app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///app.db"
    app.run(debug=True)