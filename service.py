"""This module sets up the Flask Environment"""
import os
#from redis import Redis
from flask import Flask
#jsonify, request, url_for

# Create Flask application environment
PORT = os.getenv('port', '5000')
HOST = os.getenv('HOSTNAME', '127.0.0.1')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')

app = Flask(__name__)


@app.route('/')
def index():
    """This is an example service"""
    return 'Wishlist SERVICE'

if __name__ == '__main__':
    #redis_server = redis.Redis(host=HOST, port=int(REDIS_PORT))
    app.run(host='0.0.0.0', port=int(PORT))
#testing
