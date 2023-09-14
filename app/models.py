
from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import enum

class Perms (enum.IntEnum):
	none = 0
	view = 1
	post = 2
	edit = 3
	owner = 4
	home = 5

class PermsContain (enum.IntEnum):
	default = 0
	unset = 1
	set = 2
	unset_super = 3
	set_super = 4

class User (UserMixin, db.Model):
	__tablename__ = 'user'

	id = db.Column(db.Integer, primary_key=True)

	name = db.Column(db.String(64), index=True)
	email = db.Column(db.String(128), index=True, unique=True)

	created = db.Column(db.DateTime, default=datetime.utcnow)
	lastSeen = db.Column(db.DateTime, default=datetime.utcnow)

	password_hash = db.Column(db.String(128))

	is_admin = db.Column(db.Boolean, default=False)

	posts = db.relationship('Box')
	
	def set_password(self, new):
		self.password_hash = generate_password_hash(new)
	def check_password(self, against):
		return check_password_hash(self.password_hash, against)
	
	def get_home(self):
		return Box.query.filter(Box.perms.any(user_id=self.id, level=Perms.home)).first()

	def __repr__(self):
		return f'<User {self.name}>'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Box (db.Model):
	__tablename__ = 'box'

	id = db.Column(db.Integer, primary_key=True)

	body = db.Column(db.String(2048))
	parent_id = db.Column(db.Integer, db.ForeignKey('box.id'))
	children = db.relationship('Box')

	perms_default = db.Column(db.Integer, default=Perms.post)
	perms_contain = db.Column(db.Integer, default=PermsContain.default)

	user_creator = db.Column(db.Integer, db.ForeignKey('user.id'))

	created = db.Column(db.DateTime, index=True, default=datetime.utcnow)
	modified = db.Column(db.DateTime, default=datetime.utcnow)

	def can_edit(self, user):
		if Permission.query.filter(
			Permission.user == user, 
			Permission.box == self, 
			Permission.level >= Perms.edit
		).first() != None:
			return True
		return self.default_perms >= Perms.edit

	def __repr__(self):
		return f'<Box {self.id}>'
	
class Permission (db.Model):
	__tablename__ = 'permission'

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	box_id = db.Column(db.Integer, db.ForeignKey('box.id'))

	user = db.relationship('User', backref='perms')
	box = db.relationship('Box', backref='perms')

	level = db.Column(db.Integer)

	def get_perm(self):
		return Perms(self.level).name

	def __repr__(self):
		return f'<Perm {self.user_id} {self.box_id} :: {self.level}>'
	
class UserFollowBox (db.Model):
	__tablename__ = 'user_follow_box'

	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	box_id = db.Column(db.Integer, db.ForeignKey('box.id'))

	user = db.relationship('User', backref='follow_box')
	box = db.relationship('Box', backref='followed')

	def __repr__(self):
		return f'<Follow {self.id}>'
	
