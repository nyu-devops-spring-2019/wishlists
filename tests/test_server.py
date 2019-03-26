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

"""
Wishlist API server Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN
"""

import unittest
import os
import logging
from flask_api import status    # HTTP Status Codes
#from mock import MagicMock, patch
from app.models import Wishlist, DataValidationError, db
from .wishlist_factory import WishlistFactory
import app.server as server

DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')

######################################################################
#  T E S T   C A S E S
######################################################################
class TestWishlistServer(unittest.TestCase):
    """ Wishlist Server Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        server.app.debug = False
        server.initialize_logging(logging.INFO)
        # Set up the test database
        server.app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        """ Runs before each test """
        server.init_db()
        db.drop_all()    # clean up the last tests
        db.create_all()  # create new tables
        self.app = server.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def _create_wishlists(self, count):
        """ Factory method to create pets in bulk """
        wishlists = []
        for _ in range(count):
            test_wishlist = WishlistFactory()
            resp = self.app.post('/wishlists',
                                 json=test_wishlist.serialize(),
                                 content_type='application/json')
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED, 'Could not create test wishlist')
            new_wishlist = resp.get_json()
            test_wishlist.id = new_wishlist['id']
            wishlists.append(test_wishlist)
        return wishlists

    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data['name'], 'Wishlist Demo REST API Service')

    def test_get_pet_list(self):
        """ Get a list of Wishlists """
        self._create_wishlists(5)
        resp = self.app.get('/wishlists')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

    def test_get_wishlist(self):
        """ Get a single Wishlist """
        # get the id of a pet
        test_wishlist = self._create_wishlists(1)[0]
        resp = self.app.get('/wishlists/{}'.format(test_wishlist.id),
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data['name'], test_wishlist.name)

    def test_get_wishlist_not_found(self):
        """ Get a wishlist thats not found """
        resp = self.app.get('/wishlists/0')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_wishlist(self):
        """ Create a new wishlist """
        test_wishlist = WishlistFactory()
        resp = self.app.post('/wishlists',
                             json=test_wishlist.serialize(),
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertTrue(location != None)
        # Check the data is correct
        new_wishlist = resp.get_json()
        self.assertEqual(new_wishlist['name'], test_wishlist.name, "Names do not match")
        self.assertEqual(new_wishlist['customer_id'], test_wishlist.customer_id, "CustomerIDs do not match")

        # Check that the location header was correct
        resp = self.app.get(location,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_wishlist = resp.get_json()
        self.assertEqual(new_wishlist['name'], test_wishlist.name, "Names do not match")
        self.assertEqual(new_wishlist['customer_id'], test_wishlist.customer_id, "CustomerIDs do not match")

    def test_update_wishlistt(self):
        """ Update an existing wishlistt """
        # create a wishlist to update
        test_wishlist = WishlistFactory()
        resp = self.app.post('/wishlists',
                             json=test_wishlist.serialize(),
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        # update the pet
        new_wishlist = resp.get_json()
        new_wishlist['item_id'] = 23
        resp = self.app.put('/wishlists/{}'.format(new_wishlist['id']),
                            json=new_wishlist,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        updated_wishlist = resp.get_json()
        self.assertEqual(updated_wishlist['item_id'], 23)

    def test_delete_wishlist(self):
        """ Delete a wishlist """
        test_wishlist = self._create_wishlists(1)[0]
        resp = self.app.delete('/wishlists/{}'.format(test_wishlist.id),
                               content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        # make sure they are deleted
        resp = self.app.get('/wishlists/{}'.format(test_wishlist.id),
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)



######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
