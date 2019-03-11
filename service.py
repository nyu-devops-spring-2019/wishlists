import os
from redis import Redis
from flask import Flask
#jsonify, request, url_for

# Create Flask application environment
PORT = os.getenv('port','5000')
HOST = os.getenv('HOSTNAME','127.0.0.1')
redis_port = os.getenv('REDIS_PORT','6379')

app = Flask(__name__)

@app.route('/')
def index():
	return 'Wishlist SERVICE'

if __name__ == '__name__':
	redis_server = redis.Redis(host = HOST, port = int(redis_port))
	app.run(host='0.0.0.0',port = int(PORT))
