"""
This module contains routes without Resources
"""
from flask import abort
from flask_api import status
from flask_restful import Resource
from app.models import Wishlist

######################################################################
# PURCHASE A WISHLIST
######################################################################
class PurchaseAction(Resource):
    """ Resource to Purchase a Wishlist """
    def put(self, wishlist_id):
        """ Purchase a Wishlist """
        wishlist = Pet.find(wishlist_id)
        if not wishlist:
            abort(status.HTTP_404_NOT_FOUND, "Wishlist with id '{}' was not found.".format(wishlist_id))
        wishlist.save()
        return wishlist.serialize(), status.HTTP_200_OK
