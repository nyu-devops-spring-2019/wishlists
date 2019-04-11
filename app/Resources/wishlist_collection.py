"""
This module contains the Wishlist Collection Resource
"""
from flask import request, abort
from flask_restful import Resource
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import BadRequest
from service import app, api
from service.models import Wishlist, DataValidationError
from . import WishlistResource

class WishlistCollection(Resource):
    """ Handles all interactions with collections of Wishlists """

    def get(self):
        """ Returns all of the Wishlists """
        app.logger.info('Request to list Wishlists...')
        wishlists = []
        name = request.args.get('name')
        customer_id = request.args.get('customer_id')
        item_id = request.args.get('item_id')
        if customer_id:
            app.logger.info('Filtering by customer_id: %s', customer_id)
            wishlists = Wishlist.find_by_customer_id(customer_id)
        elif name:
            app.logger.info('Filtering by name:%s', name)
            wishlists = Wishlist.find_by_name(name)
        elif item_id:
            app.logger.info('Filtering by item_id: %s', item_id)
            wishlists = Wishlist.find_by_item_id(item_id)
        else:
            wishlists = Wishlist.all()

        app.logger.info('[%s] Wishlists returned', len(wishlists))
        results = [wishlist.serialize() for wishlist in wishlists]
        return results, status.HTTP_200_OK

    def post(self):
        """
        Creates a Wishlist

        This endpoint will create a Wishlist based the data in the body that is posted
        or data that is sent via an html form post.
        """
        app.logger.info('Request to Create a Wishlist')
        content_type = request.headers.get('Content-Type')
        if not content_type:
            abort(status.HTTP_400_BAD_REQUEST, "No Content-Type set")

        data = {}
        # Check for form submission data
        if content_type == 'application/x-www-form-urlencoded':
            app.logger.info('Processing FORM data')
            app.logger.info(type(request.form))
            app.logger.info(request.form)
            data = {
                'name': request.form['name'],
                'customer_id': request.form['customer_id'],
                'item_id': request.form['item_id']
            }
        elif content_type == 'application/json':
            app.logger.info('Processing JSON data')
            data = request.get_json()
        else:
            message = 'Unsupported Content-Type: {}'.format(content_type)
            app.logger.info(message)
            abort(status.HTTP_400_BAD_REQUEST, message)

        wishlist = Wishlist()
        try:
            wishlist.deserialize(data)
        except DataValidationError as error:
            raise BadRequest(str(error))
        wishlist.save()
        app.logger.info('Wishlist with new id [%s] saved!', wishlist.id)
        location_url = api.url_for(WishlistResource, wishlist_id=wishlist.id, _external=True)
        return wishlist.serialize(), status.HTTP_201_CREATED, {'Location': location_url}
