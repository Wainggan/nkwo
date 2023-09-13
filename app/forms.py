
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
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

class PostForm (FlaskForm):
	content = TextAreaField('body', validators=[DataRequired(), Length(min=1, max=2048)])
	perms = SelectField('permissions', default='post', choices=[('none', 'hidden'), ('view', 'show'), ('post', 'post'), ('edit', 'edit')])
	perms_contained = SelectField('contain perms', default='default', choices=[
		('default', 'none'), ('set', 'set'), ('unset', 'unset'), ('edit', 'set_super'), ('unset', 'unset_super')
	])
	submit = SubmitField('post')
