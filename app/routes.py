
from flask import render_template, request, flash, redirect, abort
from flask_login import login_required
from app import app, login, db
from app.models import User, Box, Permission, Perms, PermsContain
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse
from datetime import datetime


@app.route('/', methods=['GET'])
def index():

	from app.forms import PostForm
	form = PostForm()
	
	boxes = Box.query.order_by(Box.created.desc()).all()

	id = 0
	if not current_user.is_anonymous:
		id = current_user.get_home().id

	return render_template("index.html", form=form, posts=boxes, api=app.url_for('api_post', id=id))


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

	home_box = Box(body=f"i'm new here! hi!", perms_default=Perms.view)
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

@app.route('/box/<id>', methods=['GET'])
def box(id):
	box = Box.query.filter_by(id=int(id)).first_or_404()

	if box.check_perm(current_user) <= Perms.none:
		abort(401)

	from app.forms import PostForm
	form = PostForm()
	
	return render_template('box.html', post=box, form=form, api=app.url_for('api_post', id=id))

@app.route('/box/<id>/edit', methods=['GET'])
@login_required
def box_edit(id):
	box = Box.query.filter_by(id=int(id)).first_or_404()

	from app.forms import PostForm
	form = PostForm()

	form.content.data = box.body
	form.perms_default.data = Perms(box.perms_default).name
	form.perms_contained.data = PermsContain(box.perms_contain).name
	
	return render_template('box_edit.html', post=box, form=form, api=app.url_for('api_edit', id=id))

@app.route('/box/<id>/perms', methods=['GET', 'POST'])
@login_required
def box_perms(id):
	box = Box.query.filter_by(id=int(id)).first_or_404()

	from app.forms import SpecialPermForm
	form = SpecialPermForm()

	if form.add.data:
		form.perm_list.append_entry(None)
	elif form.validate_on_submit():
		# redirect, preserve POST
		return redirect(app.url_for('api_perms', id=id), code=307)
	
	perms = Permission.query.filter_by(box_id=box.id).all()

	for i in range(len(perms)):
		if len(form.perm_list) <= i:
			form.perm_list.append_entry(None)

		form.perm_list[i].userid.data = perms[i].user_id
		form.perm_list[i].perms.data = Perms(perms[i].level).name

	return render_template('box_perms.html', post=box, form=form, api=app.url_for('box_perms', id=id))

@app.route('/user/<id>')
def user(id):
	user = User.query.filter_by(id=int(id)).first_or_404()

	home = user.get_home()

	from app.forms import PostForm
	form = PostForm()
	
	return render_template('user.html', user=user, form=form, home=home, api=app.url_for('api_post', id=home.id))

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


@app.route('/api/post/<id>', methods=['POST'])
@login_required
def api_post(id):

	from app.forms import PostForm
	form = PostForm()

	if form.validate_on_submit():
		box_parent = Box.query.filter_by(id=int(id)).first_or_404()
		
		if box_parent.check_perm(current_user) < Perms.post:
			flash("invalid permissions - you may not post to here")
			return redirect(app.url_for('box', id=box_parent.id))


		box = Box(body=form.content.data, parent_id=id, perms_default=Perms[form.perms_default.data])

		level = Perms.owner
		# if any(p.user == current_user and p.level >= Perms.owner for p in box.perms):
		#	level = Perms.owner

		perms = Permission(user=current_user, box=box, level=level)

		db.session.add(box)
		db.session.add(perms)
		db.session.commit()

		flash("resounding success!")

		return redirect(app.url_for('box', id=box.id))

	return redirect(app.url_for('/'))

@app.route('/api/edit/<id>', methods=['POST'])
@login_required
def api_edit(id):

	from app.forms import PostForm
	form = PostForm()

	if form.validate_on_submit():
		box_parent = Box.query.filter_by(id=int(id)).first_or_404()
		
		if box_parent.check_perm(current_user) < Perms.edit:
			flash("invalid permissions - you may not edit this post")
			return redirect(app.url_for('box', id=box_parent.id))

		box = Box.query.filter_by(id=int(id)).first_or_404()

		box.body = form.content.data
		box.perms_default = Perms[form.perms_default.data]
		box.perms_contain = PermsContain[form.perms_contained.data]

		box.modified = datetime.utcnow()

		db.session.commit()

		flash("resounding success!")

		return redirect(app.url_for('box', id=box.id))

	return redirect(app.url_for('/'))

@app.route('/api/perms/<id>', methods=['POST'])
@login_required
def api_perms(id):

	from app.forms import SpecialPermForm
	form = SpecialPermForm()

	if form.validate_on_submit():
		box_parent = Box.query.filter_by(id=int(id)).first_or_404()
		
		if box_parent.check_perm(current_user) < Perms.owner:
			flash("invalid permissions - you may not modify this post's permissions")
			return redirect(app.url_for('box', id=box_parent.id))

		box = Box.query.filter_by(id=int(id)).first_or_404()

		for perm_item in form.perm_list.data:
			user = User.query.filter_by(id=int(perm_item['userid'])).first()
			if user == None: continue

			level = Perms[perm_item['perms']]

			perm = Permission.query.filter_by(user_id=user.id, box_id=box.id).first()
			if perm == None:
				perm = Permission(user_id=user.id, box_id=box.id, level=level)
				db.session.add(perm)
				continue

			perm.level = level


		db.session.commit()

		flash("resounding success!")

		return redirect(app.url_for('box', id=box.id))

	return redirect(app.url_for('/'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('error/404.html'), 404

@app.errorhandler(401)
def not_found_error(error):
    return render_template('error/404.html'), 401

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('error/500.html'), 500