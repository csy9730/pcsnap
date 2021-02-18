from myapp import app, db
from models import Tiezi, Tiezilog, Tieuser
from flask_migrate import Migrate


migrate = Migrate(app, db, render_as_batch=True)


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

