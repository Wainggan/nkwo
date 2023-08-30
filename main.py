
from app import app

if __name__ == '__main__':
	app.run('localhost', debug=True, ssl_context=('cert.pem', 'key.pem'))

