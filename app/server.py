"""
Wishlist API Controller

This modules provides a REST API for the Wishlist Model

Paths:
------
GET /wishlists - Lists all of the wishlists
GET /wishlists/{id} - Retrieves a single wishlist with the specified id
POST /wishlists - Creates a new wishlist
PUT /wishlists/{id} - Updates a single wishlist with the specified id
DELETE /wishlists/{id} - Deletes a single wishlist with the specified id
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import NotFound

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from models import Wishlist, DataValidationError

# Import Flask application
from . import app

######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)

@app.errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request(error):
    """ Handles bad reuests with 400_BAD_REQUEST """
    message = error.message or str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_400_BAD_REQUEST,
                   error='Bad Request',
                   message=message), status.HTTP_400_BAD_REQUEST

@app.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """ Handles resources not found with 404_NOT_FOUND """
    message = error.message or str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_404_NOT_FOUND,
                   error='Not Found',
                   message=message), status.HTTP_404_NOT_FOUND

@app.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)
def method_not_supported(error):
    """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
    message = error.message or str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_405_METHOD_NOT_ALLOWED,
                   error='Method not Allowed',
                   message=message), status.HTTP_405_METHOD_NOT_ALLOWED

@app.errorhandler(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
def mediatype_not_supported(error):
    """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
    message = error.message or str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                   error='Unsupported media type',
                   message=message), status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

@app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """ Handles unexpected server error with 500_SERVER_ERROR """
    message = error.message or str(error)
    app.logger.error(message)
    return jsonify(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                   error='Internal Server Error',
                   message=message), status.HTTP_500_INTERNAL_SERVER_ERROR


######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    """ Root URL response """
    return jsonify(name='Wishlist Demo REST API Service',
                   version='1.0',
                   paths=url_for('list_wishlists', _external=True)
                  ), status.HTTP_200_OK

######################################################################
# LIST ALL wishlists
######################################################################
@app.route('/wishlists', methods=['GET'])
def list_wishlists():
    """ Returns all of the wishlists """
    wishlists = []
    customer_id = request.args.get('customer_id')
    name = request.args.get('name')
    if customer_id:
        wishlists = Wishlist.find_by_customer_id(customer_id)
    elif name:
        wishlists = Wishlist.find_by_name(name)
    else:
        wishlists = Wishlist.all()

    results = [wishlist.serialize() for wishlist in wishlists]
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# RETRIEVE A WishList
######################################################################
@app.route('/wishlists/<int:wishlist_id>', methods=['GET'])
def get_wishlists(wishlist_id):
    """
    Retrieve a single wishlist

    This endpoint will return a wishlist based on it's id
    """
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        abort(status.HTTP_404_NOT_FOUND, "Wishlist with id '{}' was not found.".format(wishlist_id))
    return make_response(jsonify(wishlist.serialize()), status.HTTP_200_OK)

######################################################################
# ADD A NEW Wishlist
######################################################################
@app.route('/wishlists', methods=['POST'])
def create_wishlists():
    """
    Creates a wishlist

    This endpoint will create a wishlist based the data in the body that is posted
    or data that is sent via an html form post.
    """
    app.logger.info('Request to create a wishlist')
    check_content_type('application/json')
    wishlist = Wishlist()
    wishlist.deserialize(request.get_json())
    wishlist.save()
    message = wishlist.serialize()
    location_url = url_for('get_wishlists', wishlist_id=wishlist.id, _external=True)
    return make_response(jsonify(message), status.HTTP_201_CREATED,
                         {
                             'Location': location_url
                         })
######################################################################
# UPDATE AN EXISTING Wishlist
######################################################################
@app.route('/wishlists/<int:wishlist_id>', methods=['PUT'])
def update_wishlists(wishlist_id):
    """
    Update a Wishlist

    This endpoint will update a wishlist based the body that is posted
    """
    wishlist = Wishlist.find_or_404(wishlist_id)
    wishlist.deserialize(request.get_json())
    wishlist.id = wishlist_id
    wishlist.save()
    return make_response(jsonify(wishlist.serialize()), status.HTTP_200_OK)

######################################################################
# DELETE A WishList
######################################################################
@app.route('/wishlists/<int:wishlist_id>', methods=['DELETE'])
def delete_wishlists(wishlist_id):
    """
    Delete a wishlist

    This endpoint will delete a wishlist based the id specified in the path
    """
    wishlist = Wishlist.find(wishlist_id)
    if wishlist:
        wishlist.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Wishlist.init_db(app)

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers['Content-Type'] == content_type:
        return
    app.logger.error('Invalid Content-Type: %s', request.headers['Content-Type'])
    abort(415, 'Content-Type must be {}'.format(content_type))

def initialize_logging(log_level=logging.INFO):
    """ Initialized the default logging to STDOUT """
    if not app.debug:
        print 'Setting up logging...'
        # Set up default logging for submodules to use STDOUT
        # datefmt='%m/%d/%Y %I:%M:%S %p'
        fmt = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        logging.basicConfig(stream=sys.stdout, level=log_level, format=fmt)
        # Make a new log handler that uses STDOUT
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt))
        handler.setLevel(log_level)
        # Remove the Flask default handlers and use our own
        handler_list = list(app.logger.handlers)
        for log_handler in handler_list:
            app.logger.removeHandler(log_handler)
        app.logger.addHandler(handler)
        app.logger.setLevel(log_level)
        app.logger.info('Logging handler established')
