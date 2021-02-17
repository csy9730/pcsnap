import os
from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from config import DB


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy()
db.init_app(app)
bootstrap = Bootstrap()
bootstrap.init_app(app)


@app.shell_context_processor
def make_shell_context():
    from models import Tiezi, Tiezilog, Tieuser
    return dict(db=db, Tiezi=Tiezi, Tiezilog=Tiezilog, Tieuser=Tieuser)


@app.cli.command()
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

