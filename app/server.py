######################################################################
# Copyright 2016, 2017 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Wishlist Store Service with UI

Paths:
------
GET / - Displays a UI for Selenium testing
GET /wishlists - Returns a list all of the Wishlists
GET /wishlists/{id} - Returns the Wishlist with a given id number
POST /wishlists - creates a new Wishlist record in the database
PUT /wishlists/{id} - updates a Wishlist record in the database
DELETE /wishlists/{id} - deletes a Wishlist record in the database
"""

import sys
import logging
from flask import jsonify, request, json, url_for, make_response, abort
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import NotFound
from app.models import Wishlist
from . import app

# Error handlers reuire app to be initialized so we must import
# then only after we have initialized the Flask app instance
import error_handlers


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route('/healthcheck')
def healthcheck():
    """ Let them know our heart is still beating """
    return make_response(jsonify(status=200, message='Healthy'), status.HTTP_200_OK)

######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    # data = '{name: <string>, category: <string>}'
    # url = request.base_url + 'wishlists' # url_for('list_wishlists')
    # return jsonify(name='Wishlist Demo REST API Service', version='1.0', url=url, data=data), status.HTTP_200_OK
    return app.send_static_file('index.html')

######################################################################
# LIST ALL WISHLISTS
######################################################################
@app.route('/wishlists', methods=['GET'])
def list_wishlists():
    """ Returns all of the Wishlists """
    app.logger.info('Request to list Wishlists...')
    wishlists = []
    customer_id = request.args.get('customer_id')
    name = request.args.get('name')
    if customer_id:
        app.logger.info('Find by customer_id')
        wishlists = Wishlist.find_by_customer_id(customer_id)
    elif name:
        app.logger.info('Find by name')
        wishlists = Wishlist.find_by_name(name)
    else:
        app.logger.info('Find all')
        wishlists = Wishlist.all()

    app.logger.info('[%s] Wishlists returned', len(wishlists))
    results = [wishlist.serialize() for wishlist in wishlists]
    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
# RETRIEVE A WISHLIST
######################################################################
@app.route('/wishlists/<wishlist_id>', methods=['GET'])
def get_wishlists(wishlist_id):
    """
    Retrieve a single Wishlist

    This endpoint will return a Wishlist based on it's id
    """
    app.logger.info("Request to Retrieve a wishlist with id [%s]", wishlist_id)
    wishlist =  Wishlist.find(wishlist_id)
    if not wishlist:
        raise NotFound("Wishlist with id '{}' was not found.".format(wishlist_id))
    return make_response(jsonify(wishlist.serialize()), status.HTTP_200_OK)

######################################################################
# CREATE A NEW WISHLIST  
######################################################################
@app.route('/wishlists', methods=['POST'])
def create_wishlists():
    """
    Creates a Wishlist
    This endpoint will create a Wishlist based the data in the body that is posted
    """
    app.logger.info('Request to Create a Wishlist...')
    data = {}
    # Check for form submission data
    if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
        app.logger.info('Getting data from form submit')
        data = {
            'name': request.form['name'],
            'customer_id': request.form['customer_id']
        }
    else:
        check_content_type('application/json')
        app.logger.info('Getting json data from API call')
        data = request.get_json()
    app.logger.info(data)
    wishlist = Wishlist()
    wishlist.deserialize(data)
    wishlist.save()
    app.logger.info('Wishlist with new id [%s] saved!', wishlist.id)
    message = wishlist.serialize()
    location_url = url_for('get_wishlists', wishlist_id=wishlist.id, _external=True)
    return make_response(jsonify(message), status.HTTP_201_CREATED,
                         {'Location': location_url})


######################################################################
# UPDATE AN EXISTING WISHLIST
######################################################################
@app.route('/wishlists/<wishlist_id>', methods=['PUT'])
def update_wishlists(wishlist_id):
    """
    Update a Wishlist

    This endpoint will update a Wishlist based the body that is posted
    """
    app.logger.info('Request to Update a wishlist with id [%s]', wishlist_id)
    check_content_type('application/json')
    wishlist = Wishlist.find(wishlist_id)
    if not wishlist:
        raise NotFound("Wishlist with id '{}' was not found.".format(wishlist_id))
    data = request.get_json()
    app.logger.info(data)
    wishlist.deserialize(data)
    wishlist.id = wishlist_id
    wishlist.save()
    return make_response(jsonify(wishlist.serialize()), status.HTTP_200_OK)

######################################################################
# DELETE A WISHLIST
######################################################################
@app.route('/wishlists/<wishlist_id>', methods=['DELETE'])
def delete_wishlists(wishlist_id):
    """
    Delete a Wishlist

    This endpoint will delete a Wishlist based the id specified in the path
    """
    app.logger.info('Request to Delete a wishlist with id [%s]', wishlist_id)
    wishlist = Wishlist.find(wishlist_id)
    if wishlist:
        wishlist.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
# PURCHASE A PET
######################################################################
#@app.route('/pets/<pet_id>/purchase', methods=['PUT'])
#def purchase_pets(pet_id):
#    """ Purchasing a Pet makes it unavailable """
#   pet = Pet.find(pet_id)
#    if not pet:
#        abort(status.HTTP_404_NOT_FOUND, "Pet with id '{}' was not found.".format(pet_id))
#    if not pet.available:
#        abort(status.HTTP_400_BAD_REQUEST, "Pet with id '{}' is not available.".format(pet_id))
#    pet.available = False
#    pet.save()
#    return make_response(jsonify(pet.serialize()), status.HTTP_200_OK)


######################################################################
# DELETE ALL WISHLIST DATA (for testing only)
######################################################################
@app.route('/wishlists/reset', methods=['DELETE'])
def wishlists_reset():
    """ Removes all wishlists from the database """
    Wishlist.remove_all()
    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

@app.before_first_request
def init_db(dbname="wishlists"):
    """ Initlaize the model """
    Wishlist.init_db(dbname)

# load sample data
def data_load(payload):
    """ Loads a Wishlist into the database """
    wishlist = Wishlist(payload['name'], payload['customer_id'])
    wishlist.save()

def data_reset():
    """ Removes all Wishlists from the database """
    Wishlist.remove_all()

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if 'Content-Type' not in request.headers:
        app.logger.error('No Content-Type specified.')
        abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, 'Content-Type must be {}'.format(content_type))

    if request.headers['Content-Type'] == content_type:
        return

    app.logger.error('Invalid Content-Type: %s', request.headers['Content-Type'])
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, 'Content-Type must be {}'.format(content_type))

#@app.before_first_request
def initialize_logging(log_level=app.config['LOGGING_LEVEL']):
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
