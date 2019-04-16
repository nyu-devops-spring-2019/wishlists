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
Wishlist Test Suite

Test cases can be run with the following:
nosetests -v --with-spec --spec-color
"""

# import os
# import json
import unittest
from mock import MagicMock, patch
from requests import HTTPError, ConnectionError
from service.models import Wishlist, DataValidationError



######################################################################
#  T E S T   C A S E S
######################################################################
class TestWishlists(unittest.TestCase):
    """ Test Cases for Wishlist Model """

    def setUp(self):
        """ Initialize the Cloudant database """
        Wishlist.init_db("test")
        Wishlist.remove_all()

    def test_create_a_wishlist(self):
        """ Create a wishlist and assert that it exists """
        wishlist = Wishlist("fido", "1")
        self.assertNotEqual(wishlist, None)
        self.assertEqual(wishlist.id, None)
        self.assertEqual(wishlist.name, "fido")
        self.assertEqual(wishlist.customer_id, "1")
 

    def test_add_a_wishlist(self):
        """ Create a wishlist and add it to the database """
        wishlists = Wishlist.all()
        self.assertEqual(wishlists, [])
        wishlist = Wishlist("fido", "1")
        self.assertNotEqual(wishlist, None)
        self.assertEqual(wishlist.id, None)
        wishlist.save()
        # Asert that it was assigned an id and shows up in the database
        self.assertNotEqual(wishlist.id, None)
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)
        self.assertEqual(wishlists[0].name, "fido")
        self.assertEqual(wishlists[0].customer_id, "1")


    def test_update_a_wishlist(self):
        """ Update a Wishlist """
        wishlist = Wishlist("fido", "1")
        wishlist.save()
        self.assertNotEqual(wishlist.id, None)
        # Change it an save it
        wishlist.customer_id = "k9"
        wishlist.save()
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        wishlists = Wishlist.all()
        self.assertEqual(len(wishlists), 1)
        self.assertEqual(wishlists[0].customer_id, "k9")
        self.assertEqual(wishlists[0].name, "fido")

    def test_delete_a_wishlist(self):
        """ Delete a Wishlist """
        wishlist = Wishlist("fido", "1")
        wishlist.save()
        self.assertEqual(len(Wishlist.all()), 1)
        # delete the wishlist and make sure it isn't in the database
        wishlist.delete()
        self.assertEqual(len(Wishlist.all()), 0)

    def test_serialize_a_wishlist(self):
        """ Serialize a Wishlist """
        wishlist = Wishlist("fido", "1")
        data = wishlist.serialize()
        self.assertNotEqual(data, None)
        self.assertNotIn('_id', data)
        self.assertIn('name', data)
        self.assertEqual(data['name'], "fido")
        self.assertIn('customer_id', data)
        self.assertEqual(data['customer_id'], "1")


    def test_deserialize_a_wishlist(self):
        """ Deserialize a Wishlist """
        data = {"name": "Bags", "customer_id": "1"}
        wishlist = Wishlist()
        wishlist.deserialize(data)
        self.assertNotEqual(wishlist, None)
        self.assertEqual(wishlist.id, None)
        self.assertEqual(wishlist.name, "Bags")
        self.assertEqual(wishlist.customer_id, "1")

    def test_deserialize_with_no_name(self):
        """ Deserialize a Wishlist that has no name """
        data = {"id":0, "customer_id":"2"}
        wishlist = Wishlist()
        self.assertRaises(DataValidationError, wishlist.deserialize, data)

    def test_deserialize_with_no_data(self):
        """ Deserialize a Wishlist that has no data """
        wishlist = Wishlist()
        self.assertRaises(DataValidationError, wishlist.deserialize, None)

    def test_deserialize_with_bad_data(self):
        """ Deserialize a Wishlist that has bad data """
        wishlist = Wishlist()
        self.assertRaises(DataValidationError, wishlist.deserialize, "string data")

    def test_save_a_wishlist_with_no_name(self):
        """ Save a Wishlist with no name """
        wishlist = Wishlist(None, "1")
        self.assertRaises(DataValidationError, wishlist.save)

    def test_create_a_wishlist_with_no_name(self):
        """ Create a Wishlist with no name """
        wishlist = Wishlist(None, "2")
        self.assertRaises(DataValidationError, wishlist.create)

    def test_find_wishlist(self):
        """ Find a Wishlist by id """
        Wishlist("fido", "2").save()
        saved_wishlist = Wishlist("Bags", "1")
        saved_wishlist.save()
        wishlist = Wishlist.find(saved_wishlist.id)
        self.assertIsNot(wishlist, None)
        self.assertEqual(wishlist.id, saved_wishlist.id)
        self.assertEqual(wishlist.name, "Bags")

    def test_find_with_no_wishlists(self):
        """ Find a Wishlist with empty database """
        wishlist = Wishlist.find("1")
        self.assertIs(wishlist, None)

    def test_wishlist_not_found(self):
        """ Find a Wishlist that doesnt exist """
        Wishlist("fido", "1").save()
        wishlist = Wishlist.find("2")
        self.assertIs(wishlist, None)

    def test_find_by_name(self):
        """ Find a Wishlist by Name """
        Wishlist("fido", "1").save()
        Wishlist("Bags", "2").save()
        wishlists = Wishlist.find_by_name("fido")
        self.assertNotEqual(len(wishlists), 0)
        self.assertEqual(wishlists[0].customer_id, "1")
        self.assertEqual(wishlists[0].name, "fido")

    def test_find_by_customer_id(self):
        """ Find a Wishlist by Customer_id """
        Wishlist("fido", "1").save()
        Wishlist("Bags", "2").save()
        wishlists = Wishlist.find_by_customer_id("1")
        self.assertNotEqual(len(wishlists), 0)
        self.assertEqual(wishlists[0].customer_id, "1")
        self.assertEqual(wishlists[0].name, "fido")



    def test_create_query_index(self):
        """ Test create query index """
        Wishlist("fido", "1").save()
        Wishlist("bags", "2").save()
        Wishlist.create_query_index('customer_id')

    def test_disconnect(self):
        """ Test Disconnet """
        Wishlist.disconnect()
        wishlist = Wishlist("fido", "1")
        self.assertRaises(AttributeError, wishlist.save)

    @patch('cloudant.database.CloudantDatabase.create_document')
    def test_http_error(self, bad_mock):
        """ Test a Bad Create with HTTP error """
        bad_mock.side_effect = HTTPError()
        wishlist = Wishlist("fido", "1")
        wishlist.create()
        self.assertIsNone(wishlist.id)

    @patch('cloudant.document.Document.exists')
    def test_document_not_exist(self, bad_mock):
        """ Test a Bad Document Exists """
        bad_mock.return_value = False
        wishlist = Wishlist("fido", "1")
        wishlist.create()
        self.assertIsNone(wishlist.id)

    @patch('cloudant.database.CloudantDatabase.__getitem__')
    def test_key_error_on_update(self, bad_mock):
        """ Test KeyError on update """
        bad_mock.side_effect = KeyError()
        wishlist = Wishlist("fido", "1")
        wishlist.save()
        wishlist.name = 'Fifi'
        wishlist.update()
        #self.assertEqual(pet.name, 'fido')

    @patch('cloudant.database.CloudantDatabase.__getitem__')
    def test_key_error_on_delete(self, bad_mock):
        """ Test KeyError on delete """
        bad_mock.side_effect = KeyError()
        wishlist = Wishlist("fido", "1")
        wishlist.create()
        wishlist.delete()

    @patch('cloudant.client.Cloudant.__init__')
    def test_connection_error(self, bad_mock):
        """ Test Connection error handler """
        bad_mock.side_effect = ConnectionError()
        self.assertRaises(AssertionError, Wishlist.init_db, 'test')


#     def test_http_error(self):
    # @patch.dict(os.environ, {'VCAP_SERVICES': json.dumps(VCAP_SERVICES)})
    # def test_vcap_services(self):
    #     """ Test if VCAP_SERVICES works """
    #     Pet.init_db()
    #     self.assertIsNotNone(Pet.client)
    #     Pet("fido", "dog", True).save()
    #     pets = Pet.find_by_name("fido")
    #     self.assertNotEqual(len(pets), 0)
    #     self.assertEqual(pets[0].name, "fido")


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestWishlists)
    unittest.TextTestRunner(verbosity=2).run(suite)
