
from flask import request
from app import app

def redirect_url(default='index'):
	return request.args.get('next') or \
		request.referrer or \
		app.url_for(default)

