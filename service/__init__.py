"""
Package: app

Package for the application models and services
This module also sets up the logging to be used with gunicorn
"""
import os
import sys
import logging
from flask import Flask
from flask_restful import Api 
from .models import Wishlist, DataValidationError

# Create Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'please, tell nobody... Shhhh'
app.config['LOGGING_LEVEL'] = logging.INFO

api = Api(app)

from service.resources import WishlistResource
from service.resources import WishlistCollection
from service.resources import HomePage
#from app.resources import PurchaseAction


api.add_resource(HomePage, '/')
api.add_resource(WishlistCollection, '/wishlists')
api.add_resource(WishlistResource, '/wishlists/<wishlist_id>')
#api.add_resource(PurchaseAction, 'wishlists/<wishlist_id>/purchase')


# Set up logging for production
print 'Setting up logging for {}...'.format(__name__)
if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    if gunicorn_logger:
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)

app.logger.info('************************************************************')
app.logger.info('        W I S H L I S T   R E S T   A P I   S E R V I C E ')
app.logger.info('************************************************************')
app.logger.info('Logging established')


@app.before_first_request
def init_db(dbname="wishlists"):
    """ Initlaize the model """
    Wishlist.init_db(dbname)
