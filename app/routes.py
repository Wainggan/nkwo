
from flask import render_template, request, flash, redirect
from flask_login import login_required
from app import app, login, db
from app.models import User, Box, Permission, Perms
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse
from datetime import datetime


@app.route('/', methods=['GET', 'POST'])
def index():

	from app.forms import PostForm
	form = PostForm()

	if form.validate_on_submit():
		box = Box(body=form.content.data, parent_id=current_user.get_home().id, default_perms=Perms[form.perms.data])

		perms = Permission(user=current_user, box=box, level=Perms.owner)

		db.session.add(box)
		db.session.add(perms)
		db.session.commit()

		flash("resounding success!")

		return redirect(app.url_for('box', id=box.id))
	
	boxes = Box.query.order_by(Box.created.desc()).all()

	return render_template("index.html", form=form, posts=boxes)


@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect('/')
	
	from app.forms import LoginForm
	form = LoginForm()

	if request.method == "GET":
		return render_template('login.html', form=form)
	if not form.validate_on_submit():
		flash(f"invalid form")
		return render_template('login.html', form=form)
	
	from email_validator import validate_email, ValidatedEmail
	try:
		v = validate_email(form.email.data, check_deliverability=False)
	except:
		flash(f"invalid email")
		return render_template('login.html', form=form)

	email = v.normalized
	
	user: User = User.query.filter_by(email=email).first()
	if user is None:
		flash(f"email not in use")
		return render_template('login.html', form=form)
	if not user.check_password(form.password.data):
		flash(f"incorrect password")
		return render_template('login.html', form=form)
	
	login_user(user, remember=form.remember.data)

	print(f"attempting login: {email}")
	flash(f"successfully logged in")

	next_page = request.args.get('next')
	if not next_page or url_parse(next_page).netloc != '':
		next_page = app.url_for('index')

	return redirect(next_page)

@app.route('/register', methods=['GET', 'POST'])
def signup():
	if current_user.is_authenticated:
		return redirect(app.url_for('index'))
	
	from app.forms import SignupForm
	form = SignupForm()

	if request.method == "GET":
		return render_template('signup.html', form=form)
	if not form.validate_on_submit():
		flash(f"invalid form")
		return render_template('signup.html', form=form)

	user = User(name=form.name.data, email=form.email.data)
	user.set_password(form.password.data)

	home_box = Box(body=f"i'm new here! hi!", default_perms=Perms.view)
	db.session.add(home_box)
	db.session.add(user)

	perms = Permission(user=user, box=home_box, level=Perms.home)
	db.session.add(perms)
	db.session.commit()

	flash('resounding success!!')
	return redirect(app.url_for('login'))

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.lastSeen = datetime.utcnow()
        db.session.commit()

@app.route('/logout')
def logout():
	logout_user()
	return redirect('/')

@app.route('/box/<id>', methods=['GET', 'POST'])
def box(id):
	box = Box.query.filter_by(id=int(id)).first_or_404()

	from app.forms import PostForm
	form = PostForm()

	if form.validate_on_submit():
		childbox = Box(body=form.content.data, parent_id=box.id, default_perms=Perms[form.perms.data])

		level = Perms.edit
		if any(p.user == current_user and p.level >= Perms.owner for p in box.perms):
			level = Perms.owner

		perms = Permission(user=current_user, box=childbox, level=level)

		db.session.add(childbox)
		db.session.add(perms)
		db.session.commit()

		flash("resounding success!")

		return redirect(request.url)
	
	return render_template('box.html', post=box, form=form)

@app.route('/user/<id>')
def user(id):
	user = User.query.filter_by(id=int(id)).first_or_404()

	home = user.get_home()

	from app.forms import PostForm
	form = PostForm()
	
	return render_template('user.html', user=user, home=home, form=form)

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():

	from app.forms import SettingsForm
	form = SettingsForm()

	if form.validate_on_submit():
		current_user.name = form.name.data
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(app.url_for('settings'))
	elif request.method == 'GET':
		form.name.data = current_user.name

	return render_template('settings.html', form=form)



@app.errorhandler(404)
def not_found_error(error):
    return render_template('error/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error/500.html'), 500