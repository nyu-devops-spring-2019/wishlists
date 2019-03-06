


from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
	return 'Hello Wishlist'


if __name__ == '__name__':
	app.run()
