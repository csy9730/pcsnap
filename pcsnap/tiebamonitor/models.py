# -*- coding: utf-8 -*-
"""User models."""
import datetime as dt

from flask_login import UserMixin

from sqlalchemy import Column, String, Integer, create_engine, Boolean, Float
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import ForeignKey  # , relationship

from myapp import db 
Base = db.Model
# Base = declarative_base()


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
