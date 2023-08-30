
from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flaskext.markdown import Markdown

app = Flask(__name__)
app.config.from_object(Config)

login = LoginManager(app)

db = SQLAlchemy(app)

migrate = Migrate(app, db)

markdown = Markdown(app)

from app import routes, models
