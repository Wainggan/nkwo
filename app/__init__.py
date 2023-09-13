
from flask import Flask
from config import Config
from instance.config import InstanceConfig
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

from flaskext.markdown import Markdown
from mdx_bleach.extension import BleachExtension, ALLOWED_TAGS

app = Flask(__name__)
app.config.from_object(Config)
app.config.from_object(InstanceConfig)

login = LoginManager(app)

db = SQLAlchemy(app)

migrate = Migrate(app, db)

bleach = BleachExtension(tags=ALLOWED_TAGS)
markdown = Markdown(app, extensions=[bleach])

from app import routes, models
