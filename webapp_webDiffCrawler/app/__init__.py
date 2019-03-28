from flask import Flask, render_template
# Flask extensions imports
from flask_bootstrap import Bootstrap
from flask_moment import Moment

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# import webapp.forms

from webapp_webDiffCrawler.config import config



bootstrap = Bootstrap()  # Bootstrap extension initialization
moment = Moment()  # Extension that uses the Moment.js library to convert UTC time to client time

# SQLAlchemy attributes
engine = None
DBSession = None
dbSession = None


def create_app(config_name):
    global engine, DBSession, dbSession

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    moment.init_app(app)

    # SQLAlchemy attributes
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'], echo=True)
    DBSession = sessionmaker(bind=engine)
    dbSession = DBSession()

    # Register the main blueprint
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app