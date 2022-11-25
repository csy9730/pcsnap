import os
import datetime
import json
from flask import Flask, render_template, request
from flask_restful import reqparse, abort, Api, Resource
from flask_bootstrap import Bootstrap

from sqlalchemy import Column, String, Integer, create_engine, Boolean, Float, Text
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


class Person(db.Model):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True)
    name = Column(String(260))
    card_id = Column(String(20), nullable=True)
    is_female = Column(Boolean(), default=False)
    is_alive = Column(Boolean, default=True)
    birth_year = Column(Integer, nullable=True)
    birth_date = Column(Integer, nullable=True)
    spouse_id = Column(Integer, ForeignKey("person.id"))
    married = Column(Integer) # 0 no marry 1 married 2 cut split
    about = Column(Text())

    @property
    def _last_visit_time(self):
        return datetime.datetime(1601, 1, 1) + datetime.timedelta(microseconds=self.last_visit_time)

    def __repr__(self):
        return '<Person %s %s>' % (self.id, self.name)


class Parent(db.Model):
    __tablename__ = 'parent'
    id = Column(Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    child_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    is_depreciated = Column(Boolean(), default=False)
    def __repr__(self):
        return '<Parent %s %s>' % (self.id, self.parent_id)

class Friend(db.Model):
    __tablename__ = 'friend'
    id = Column(Integer, primary_key=True)
    friend_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    mate_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    relation = Column(Integer) # 1->relative  2->classmate 4-> workmate 8-> neighbor 16-> netizen 32->anonymous
    
    is_depreciated = Column(Boolean(), default=False)
    def __repr__(self):
        return '<Friend %s %s>' % (self.id, self.friend_id)
    # visit_count
    # last_visit_time

class Contact(db.Model):
    __tablename__ = 'contact'
    id = Column(Integer, primary_key=True)
    mobile = Column(String(40))
    email = Column(String(100))
    address = Column(String(200))
    homepage = Column(String(200))
    tag = Column(String(60))

class Visit(db.Model):
    __tablename__ = 'visit'

    id = Column(Integer, primary_key=True)
    friend_id = Column(Integer)
    timestamp = Column(String(360))
    location = Column(String(360))
    platform = Column(Integer)


@app.route('/')
def index():
    return render_template("index.html")


if __name__ == '__main__':
    # app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///app.db"
    app.run(debug=True)