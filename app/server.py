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

import sys
import logging
from flask import jsonify, request, url_for, make_response, abort
from flask_api import status    # HTTP Status Codes
from app.models import Wishlist, DataValidationError
from app import app

######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)

@app.errorhandler(400)
def bad_request(error):
    """ Handles bad reuests with 400_BAD_REQUEST """
    message = str(error)
    app.logger.info(message)
    return jsonify(status=400, error='Bad Request', message=message), 400

@app.errorhandler(404)
def not_found(error):
    """ Handles resources not found with 404_NOT_FOUND """
    message = str(error)
    app.logger.info(message)
    return jsonify(status=404, error='Not Found', message=message), 404

@app.errorhandler(405)
def method_not_supported(error):
    """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
    message = str(error)
    app.logger.info(message)
    return jsonify(status=405, error='Method not Allowed', message=message), 405

@app.errorhandler(415)
def mediatype_not_supported(error):
    """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
    message = str(error)
    app.logger.info(message)
    return jsonify(status=415, error='Unsupported media type', message=message), 415

@app.errorhandler(500)
def internal_server_error(error):
    """ Handles unexpected server error with 500_SERVER_ERROR """
    message = str(error)
    app.logger.info(message)
    return jsonify(status=500, error='Internal Server Error', message=message), 500

######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    """ Send back the home page """
    return app.send_static_file('index.html')

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

@app.route('/wishlists/sorted', methods=['GET'])
def list_sorted():
    """ Returns all of the wishlists """
    wishlists = []
    wishlists = Wishlist.all_sorted()

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
    data = {}
    # Check for form submission data
    if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
        app.logger.info('Processing FORM data')
        data = {
            'name': request.form['name'],
            'description': request.form['description'],
            'customer_id': request.form['customer_id'],
            'item_id': request.form['item_id']#todo, change this to a lit
        }
    else:
        app.logger.info('Processing JSON data')
        data = request.get_json()
    wishlist = Wishlist()
    wishlist.deserialize(data)
    wishlist.save()
    message = wishlist.serialize()
    return make_response(jsonify(message), status.HTTP_201_CREATED,
                         {'Location': url_for('get_wishlist', wishlist_id=wishlist.id, _external=True)})

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
    Wishlist.init_db()

#@app.before_first_request
def initialize_logging(log_level=logging.INFO):
    """ Initialized the default logging to STDOUT """
    if not app.debug:
        print('Setting up logging...')
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
