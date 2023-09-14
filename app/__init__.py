
from flask import Flask

from config import Config
from instance.config import InstanceConfig

from flaskext.markdown import Markdown
from mdx_bleach.extension import BleachExtension, ALLOWED_TAGS

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import MetaData

from flask_login import LoginManager



app = Flask(__name__)
app.config.from_object(Config)
app.config.from_object(InstanceConfig)

login = LoginManager(app)

convention = {
	"ix": "ix_%(column_0_label)s",
	"uq": "uq_%(table_name)s_%(column_0_name)s",
	"ck": "ck_%(table_name)s_%(constraint_name)s",
	"fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
	"pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(app, metadata=metadata)

migrate = Migrate(app, db)

bleach = BleachExtension(tags=ALLOWED_TAGS)
markdown = Markdown(app, extensions=[bleach])

from app import routes, models
