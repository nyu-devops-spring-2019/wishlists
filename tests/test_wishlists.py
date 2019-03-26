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
Test cases for Wishlist Model

Test cases can be run with:
  nosetests
  coverage report -m
"""

import unittest
import os
from app.models import Wishlist, DataValidationError, db
from app import app

DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')

######################################################################
#  T E S T   C A S E S
######################################################################
class TestWishlists(unittest.TestCase):
    """ Test Cases for Wishlists """

    @classmethod
    def setUpClass(cls):
        """ These run once per Test suite """
        app.debug = False
        # Set up the test database
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        Wishlist.init_db(app)
        db.drop_all()    # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_a_wishlist(self):
        """ Create a wishlist and assert that it exists """
        wishlist = Wishlist(name="shoes", item_id=3, customer_id=5)
        self.assertTrue(wishlist != None)
        self.assertEqual(wishlist.id, None)
        self.assertEqual(wishlist.name, "shoes")
        self.assertEqual(wishlist.item_id, 3)

    def test_add_a_wishlist(self):
        """ Create a wishlist and add it to the database """
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])
        wishlist = Wishlist(name="shoes", item_id=45, customer_id=88)
        self.assertTrue(wishlist != None)
        self.assertEqual(wishlist.id, None)
        wishlist.save()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual(wishlist.id, 1)
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)

    def test_update_a_wishlist(self):
        """ Update a wishlist """
        wishlist = Wishlist(name="shoes", item_id=45, customer_id=88)
        wishlist.save()
        self.assertEqual(wishlist.id, 1)
        # Change it an save it
        wishlist.name = "sneakers"
        wishlist.save()
        self.assertEqual(wishlist.id, 1)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)
        self.assertEqual(wishlists[0].name, "sneakers")

    def test_delete_a_wishlist(self):
        """ Delete a Wishlist """
        wishlist = Wishlist(name="shoes", item_id=45, customer_id=88)
        wishlist.save()
        self.assertEqual(len(Wishlist.all()), 1)
        # delete the wishlist and make sure it isn't in the database
        wishlist.delete()
        self.assertEqual(len(Wishlist.all()), 0)

    def test_serialize_a_pet(self):
        """ Test serialization of a Pet """
        wishlist = Wishlist(name="shoes", item_id=45, customer_id=88)
        data = wishlist.serialize()
        self.assertNotEqual(data, None)
        self.assertIn('id', data)
        self.assertEqual(data['id'], None)
        self.assertIn('name', data)
        self.assertEqual(data['name'], "shoes")

    def test_deserialize_a_pet(self):
        """ Test deserialization of a Pet """
        data = {"id": 1, "name": "shoes", "customer_id": 33, "item_id": 32}
        wishlist = Wishlist()
        wishlist.deserialize(data)
        self.assertNotEqual(wishlist, None)
        self.assertEqual(wishlist.id, None)
        self.assertEqual(wishlist.name, "shoes")
        self.assertEqual(wishlist.customer_id, 33)

    def test_deserialize_bad_data(self):
        """ Test deserialization of bad data """
        data = "this is not a dictionary"
        wishlist = Wishlist()
        self.assertRaises(DataValidationError, wishlist.deserialize, data)

    def test_find_wishlist(self):
        """ Find a wishlist by ID """
        Wishlist(name="shoes", item_id=45, customer_id=88).save()
        wish = Wishlist(name="sandals", item_id=425, customer_id=88)
        wish.save()
        example = Wishlist.find(wish.id)
        self.assertIsNot(example, None)
        self.assertEqual(example.name, "sandals")


    def test_find_by_name(self):
        """ Find a wishlist by Name """
        Wishlist(name="shoes", item_id=45, customer_id=88).save()
        Wishlist(name="sandals", item_id=435, customer_id=828).save()
        wishlists = Wishlist.find_by_name("shoes")
        self.assertEqual(wishlists[0].item_id, 45)
        self.assertEqual(wishlists[0].name, "shoes")

    def test_find_by_item_id(self):
        """ Find a wishlist by item_id """
        Wishlist(name="shoes", item_id=45, customer_id=88).save()
        Wishlist(name="sandals", item_id=435, customer_id=828).save()
        wishlists = Wishlist.find_by_item_id(45)
        self.assertEqual(wishlists[0].item_id, 45)
        self.assertEqual(wishlists[0].name, "shoes")

    def test_find_by_customer_id(self):
        """ Find a wishlist by customer_id """
        Wishlist(name="shoes", item_id=45, customer_id=88).save()
        Wishlist(name="sandals", item_id=435, customer_id=828).save()
        wishlists = Wishlist.find_by_customer_id(88)
        self.assertEqual(wishlists[0].item_id, 45)
        self.assertEqual(wishlists[0].name, "shoes")

######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
