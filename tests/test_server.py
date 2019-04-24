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
Wishlist API Service Test Suite

Test cases can be run with the following:
nosetests -v --with-spec --spec-color
"""
import unittest
import json
from werkzeug.datastructures import MultiDict, ImmutableMultiDict
from service import app
from service.models import Wishlist

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_405_METHOD_NOT_ALLOWED = 405
HTTP_409_CONFLICT = 409

######################################################################
#  T E S T   C A S E S
######################################################################
class TestWishlistServer(unittest.TestCase):
    """ Wishlist Service tests """

    def setUp(self):
        """ Initialize the Cloudant database """
        self.app = app.test_client()
        Wishlist.init_db("tests")
        Wishlist.remove_all()
        Wishlist("fido", "1").save()
        Wishlist("Bags to buy", "2").save()
        Wishlist("Summer outfit", "3").save()

    def test_index(self):
        """ Test the index page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertIn('Wishlist Demo REST API Service', resp.data)

    def test_get_wishlist_list(self):
        """ Get a list of Wishlists """
        resp = self.app.get('/wishlists')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertTrue(len(resp.data) > 0)

    def test_get_wishlist(self):
        """ get a single Wishlist """
        wishlist = self.get_wishlist('Summer outfit')[0] # returns a list
        resp = self.app.get('/wishlists/{}'.format(wishlist['id']))
        self.assertEqual(resp.status_code, HTTP_200_OK)
        data = json.loads(resp.data)
        self.assertEqual(data['name'], 'Summer outfit')

    def test_get_wishlist_not_found(self):
        """ Get a Wishlist that doesn't exist """
        resp = self.app.get('/wishlists/0')
        self.assertEqual(resp.status_code, HTTP_404_NOT_FOUND)
        data = json.loads(resp.data)
        self.assertIn('was not found', data['message'])

    def test_create_wishlist(self):
        """ Create a new Wishlist """
        # save the current number of wishlists for later comparrison
        wishlist_count = self.get_wishlist_count()
        # add a new wishlist
        new_wishlist = {'name': 'Bags', 'customer_id': '1'}
        data = json.dumps(new_wishlist)
        resp = self.app.post('/wishlists', data=data, content_type='application/json')
        # if resp.status_code == 429: # rate limit exceeded
        #     sleep(1)                # wait for 1 second and try again
        #     resp = self.app.post('/wishlists', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertNotEqual(location, None)
        # Check the data is correct
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['name'], 'Bags')
        # check that count has gone up and includes Bags
        resp = self.app.get('/wishlists')
        data = json.loads(resp.data)
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertEqual(len(data), wishlist_count + 1)
        self.assertIn(new_json, data)

    def test_create_wishlist_from_formdata(self):
        wishlist_data = MultiDict()
        wishlist_data.add('name', 'Timothy')
        wishlist_data.add('customer_id', '3')
        data = ImmutableMultiDict(wishlist_data)
        resp = self.app.post('/wishlists', data=data, content_type='application/x-www-form-urlencoded')
        self.assertEqual(resp.status_code, HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertNotEqual(location, None)
        # Check the data is correct
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['name'], 'Timothy')

    def test_update_wishlist(self):
        """ Update a Wishlist """
        wishlist = self.get_wishlist('fido')[0] # returns a list
        self.assertEqual(wishlist['customer_id'], '1')
        wishlist['customer_id'] = '4'
        # make the call
        data = json.dumps(wishlist)
        resp = self.app.put('/wishlists/{}'.format(wishlist['id']), data=data,
                            content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        # go back and get it again
        resp = self.app.get('/wishlists/{}'.format(wishlist['id']), content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['customer_id'], '4')

    def test_update_wishlist_with_no_name(self):
        """ Update a Wishlist without assigning a name """
        wishlist = self.get_wishlist('fido')[0] # returns a list
        del wishlist['name']
        data = json.dumps(wishlist)
        resp = self.app.put('/wishlists/{}'.format(wishlist['id']), data=data,
                            content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)

    def test_update_wishlist_not_found(self):
        """ Update a Wishlist that doesn't exist """
        new_bag = {"name": "Bags", "customer_id": "6"}
        data = json.dumps(new_bag)
        resp = self.app.put('/wishlists/0', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_404_NOT_FOUND)

    def test_delete_wishlist(self):
        """ Delete a Wishlist """
        wishlist = self.get_wishlist('fido')[0] # returns a list
        # save the current number of wishlists for later comparrison
        wishlist_count = self.get_wishlist_count()
        # delete a wishlist
        resp = self.app.delete('/wishlists/{}'.format(wishlist['id']), content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        new_count = self.get_wishlist_count()
        self.assertEqual(new_count, wishlist_count - 1)

    def test_create_wishlist_with_no_name(self):
        """ Create a Wishlist without a name """
        new_wishlist = {'customer_id': '9'}
        data = json.dumps(new_wishlist)
        resp = self.app.post('/wishlists', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)

    def test_create_wishlist_no_content_type(self):
        """ Create a Wishlist with no Content-Type """
        new_wishlist = {'name': 'Bags', 'customer_id': '11'}
        data = json.dumps(new_wishlist)
        resp = self.app.post('/wishlists', data=data)
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)

    def test_create_wishlist_wrong_content_type(self):
        """ Create a Wishlist with wrong Content-Type """
        data = "jimmy the fish"
        resp = self.app.post('/wishlists', data=data, content_type='plain/text')
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)

    def test_call_create_with_an_id(self):
        """ Call create passing an id """
        new_wishlist = {'name': 'Bags', 'customer_id': '5'}
        data = json.dumps(new_wishlist)
        resp = self.app.post('/wishlists/1', data=data)
        self.assertEqual(resp.status_code, HTTP_405_METHOD_NOT_ALLOWED)

    def test_query_by_name(self):
        """ Query Wishlist by name """
        resp = self.app.get('/wishlists', query_string='name=fido')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertTrue(len(resp.data) > 0)
        self.assertIn('fido', resp.data)
        self.assertNotIn('Bags', resp.data)
        data = json.loads(resp.data)
        query_item = data[0]
        self.assertEqual(query_item['name'], 'fido')

    def test_query_by_customer_id(self):
        """ Query Wishlists by customer_id """
        resp = self.app.get('/wishlists', query_string='customer_id=1')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertTrue(len(resp.data) > 0)
        self.assertIn('fido', resp.data)
        self.assertNotIn('kitty', resp.data)
        data = json.loads(resp.data)
        query_item = data[0]
        self.assertEqual(query_item['customer_id'], '1')


######################################################################
# Utility functions
######################################################################

    def get_wishlist(self, name):
        """ retrieves a wishlist for use in other actions """
        resp = self.app.get('/wishlists',
                            query_string='name={}'.format(name))
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertGreater(len(resp.data), 0)
        self.assertIn(name, resp.data)
        data = json.loads(resp.data)
        return data

    def get_wishlist_count(self):
        """ save the current number of wishlists """
        resp = self.app.get('/wishlists')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        data = json.loads(resp.data)
        return len(data)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
