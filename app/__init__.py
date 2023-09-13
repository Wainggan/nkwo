
from flask import Flask
from config import Config
from instance.config import InstanceConfig
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flaskext.markdown import Markdown

app = Flask(__name__)
app.config.from_object(Config)
app.config.from_object(InstanceConfig)

login = LoginManager(app)

db = SQLAlchemy(app)

migrate = Migrate(app, db)

markdown = Markdown(app)

from app import routes, models
