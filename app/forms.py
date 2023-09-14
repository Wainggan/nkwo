
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, FieldList, FormField
from wtforms.validators import DataRequired, Email, ValidationError, Length
from app.models import User

class LoginForm (FlaskForm):
	email = StringField('email', validators=[DataRequired()])
	password = PasswordField('password', validators=[DataRequired()])
	remember = BooleanField('remember')
	submit = SubmitField('login')

class SignupForm (FlaskForm):
	email = StringField('email', validators=[DataRequired(), Email()])
	name = StringField('name', validators=[DataRequired()])
	password = PasswordField('password', validators=[DataRequired()])
	submit = SubmitField('signup')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user != None:
			raise ValidationError("email already already in use")

class SettingsForm (FlaskForm):
	name = StringField('name', validators=[DataRequired()])
	submit = SubmitField('submit')

class SpecialPermFormItem (FlaskForm):
	userid = StringField('user id', validators=[DataRequired()])
	perms = SelectField('permissions', default='post', choices=[
		('none', 'none'), ('view', 'view'), ('post', 'post'), ('edit', 'edit'), ('owner', 'owner')
	])

	remove = SubmitField('-')

	def validate_id(self, id):
		user = User.query.filter_by(id=id.data).first()
		if user == None:
			raise ValidationError(f"user {id} does not exist")

class SpecialPermForm (FlaskForm):
	add = SubmitField('+')
	perm_list = FieldList(FormField(SpecialPermFormItem))

	submit = SubmitField('send')

	

class PostForm (FlaskForm):
	content = TextAreaField('body', validators=[DataRequired(), Length(min=1, max=2048)])
	perms_default = SelectField('permissions', default='post', choices=[
		('none', 'none'), ('view', 'view'), ('post', 'post'), ('edit', 'edit'), ('owner', 'owner')
	])
	perms_contained = SelectField('contain perms', default='default', choices=[
		('default', 'none'), ('set', 'set'), ('unset', 'unset'), ('set_super', 'set_super'), ('unset_super', 'unset_super')
	])
	
	submit = SubmitField('send')
