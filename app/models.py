######################################################################
# Copyright 2016, 2018 John Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################
"""
Wishlist Model that uses Cloudant

You must initlaize this class before use by calling inititlize().
This class looks for an environment variable called VCAP_SERVICES
to get it's database credentials from. If it cannot find one, it
tries to connect to Cloudant on the localhost. If that fails it looks
for a server name 'cloudant' to connect to.

To use with Docker couchdb database use:
    docker run -d --name couchdb -p 5984:5984 -e COUCHDB_USER=admin -e COUCHDB_PASSWORD=pass couchdb

Docker Note:
    CouchDB uses /opt/couchdb/data to store its data, and is exposed as a volume
    e.g., to use current folder add: -v $(pwd):/opt/couchdb/data
    You can also use Docker volumes like this: -v couchdb_data:/opt/couchdb/data
"""

import os
import json
import logging
from retry import retry
from cloudant.client import Cloudant
from cloudant.query import Query
from requests import HTTPError, ConnectionError

# get configruation from enviuronment (12-factor)
ADMIN_PARTY = os.environ.get('ADMIN_PARTY', 'False').lower() == 'true'
CLOUDANT_HOST = os.environ.get('CLOUDANT_HOST', 'localhost')
CLOUDANT_USERNAME = os.environ.get('CLOUDANT_USERNAME', 'admin')
CLOUDANT_PASSWORD = os.environ.get('CLOUDANT_PASSWORD', 'pass')

class DataValidationError(Exception):
    """ Custom Exception with data validation fails """
    pass

class Wishlist(object):
    """ Wishlist interface to database """

    logger = logging.getLogger(__name__)
    client = None   # cloudant.client.Cloudant
    database = None # cloudant.database.CloudantDatabase

    def __init__(self, name=None, category=None, available=True):
        """ Constructor """
        self.id = None
        self.name = name
        self.customer_id = customer_id

    @retry(HTTPError, delay=1, backoff=2, tries=5)
    def create(self):
        """
        Creates a new Wishlist in the database
        """
        if self.name is None:   # name is the only required field
            raise DataValidationError('name attribute is not set')

        try:
            document = self.database.create_document(self.serialize())
        except HTTPError as err:
            Wishlist.logger.warning('Create failed: %s', err)
            return

        if document.exists():
            self.id = document['_id']

    @retry(HTTPError, delay=1, backoff=2, tries=5)
    def update(self):
        """
        Updates a Wishlist in the database
        """
        try:
            document = self.database[self.id]
        except KeyError:
            document = None
        if document:
            document.update(self.serialize())
            document.save()

    @retry(HTTPError, delay=1, backoff=2, tries=5)
    def save(self):
        """ Saves a Wishlist in the database """
        if self.name is None:   # name is the only required field
            raise DataValidationError('name attribute is not set')
        if self.id:
            self.update()
        else:
            self.create()

    @retry(HTTPError, delay=1, backoff=2, tries=5)
    def delete(self):
        """ Deletes a Wishlist from the database """
        try:
            document = self.database[self.id]
        except KeyError:
            document = None
        if document:
            document.delete()

    def serialize(self):
        """ serializes a Wishlist into a dictionary """
        wishlist = {
            "name": self.name,
            "customer_id": self.customer_id
        }
        if self.id:
            wishlist['_id'] = self.id
        return wishlist

    def deserialize(self, data):
        """ deserializes a Wishlist my marshalling the data """
        Wishlist.logger.info(data)
        try:
            self.name = data['name']
            self.customer_id = data['customer_id']
        except KeyError as error:
            raise DataValidationError('Invalid wishlist: missing ' + error.args[0])
        except TypeError as error:
            raise DataValidationError('Invalid wishlist: body of request contained bad or no data')

        # if there is no id and the data has one, assign it
        if not self.id and '_id' in data:
            self.id = data['_id']

        return self


######################################################################
#  S T A T I C   D A T A B S E   M E T H O D S
######################################################################

    @classmethod
    def connect(cls):
        """ Connect to the server """
        cls.client.connect()

    @classmethod
    def disconnect(cls):
        """ Disconnect from the server """
        cls.client.disconnect()

    @classmethod
    @retry(HTTPError, delay=1, backoff=2, tries=5)
    def create_query_index(cls, field_name, order='asc'):
        """ Creates a new query index for searching """
        cls.database.create_query_index(index_name=field_name, fields=[{field_name: order}])

    @classmethod
    @retry(HTTPError, delay=1, backoff=2, tries=5)
    def remove_all(cls):
        """ Removes all documents from the database (use for testing)  """
        for document in cls.database:
            document.delete()

    @classmethod
    @retry(HTTPError, delay=1, backoff=2, tries=5)
    def all(cls):
        """ Query that returns all Wishlists """
        results = []
        for doc in cls.database:
            wishlist = Wishlist().deserialize(doc)
            wishlist.id = doc['_id']
            results.append(wishlist)
        return results

######################################################################
#  F I N D E R   M E T H O D S
######################################################################

    @classmethod
    @retry(HTTPError, delay=1, backoff=2, tries=5)
    def find_by(cls, **kwargs):
        """ Find records using selector """
        query = Query(cls.database, selector=kwargs)
        results = []
        for doc in query.result:
            wishlist = Wishlist()
            wishlist.deserialize(doc)
            results.append(wishlist)
        return results

    @classmethod
    @retry(HTTPError, delay=1, backoff=2, tries=5)
    def find(cls, wishlist_id):
        """ Query that finds Wishlists by their id """
        try:
            document = cls.database[wishlist_id]
            return Wishlist().deserialize(document)
        except KeyError:
            return None

    @classmethod
    @retry(HTTPError, delay=1, backoff=2, tries=5)
    def find_by_name(cls, name):
        """ Query that finds Wishlists by their name """
        return cls.find_by(name=name)

    @classmethod
    @retry(HTTPError, delay=1, backoff=2, tries=5)
    def find_by_customer_id(cls, customer_id):
        """ Query that finds Wishlists by their customer_id """
        return cls.find_by(customer_id=customer_id)



############################################################
#  C L O U D A N T   D A T A B A S E   C O N N E C T I O N
############################################################

    @staticmethod
    def init_db(dbname='wishlists'):
        """
        Initialized Coundant database connection
        """
        opts = {}
        vcap_services = {}
        # Try and get VCAP from the environment or a file if developing
        if 'VCAP_SERVICES' in os.environ:
            Wishlist.logger.info('Running in Bluemix mode.')
            vcap_services = json.loads(os.environ['VCAP_SERVICES'])
        # if VCAP_SERVICES isn't found, maybe we are running on Kubernetes?
        elif 'BINDING_CLOUDANT' in os.environ:
            Wishlist.logger.info('Found Kubernetes Bindings')
            creds = json.loads(os.environ['BINDING_CLOUDANT'])
            vcap_services = {"cloudantNoSQLDB": [{"credentials": creds}]}
        else:
            Wishlist.logger.info('VCAP_SERVICES and BINDING_CLOUDANT undefined.')
            creds = {
                "username": CLOUDANT_USERNAME,
                "password": CLOUDANT_PASSWORD,
                "host": CLOUDANT_HOST,
                "port": 5984,
                "url": "http://"+CLOUDANT_HOST+":5984/"
            }
            vcap_services = {"cloudantNoSQLDB": [{"credentials": creds}]}

        # Look for Cloudant in VCAP_SERVICES
        for service in vcap_services:
            if service.startswith('cloudantNoSQLDB'):
                cloudant_service = vcap_services[service][0]
                opts['username'] = cloudant_service['credentials']['username']
                opts['password'] = cloudant_service['credentials']['password']
                opts['host'] = cloudant_service['credentials']['host']
                opts['port'] = cloudant_service['credentials']['port']
                opts['url'] = cloudant_service['credentials']['url']

        if any(k not in opts for k in ('host', 'username', 'password', 'port', 'url')):
            Wishlist.logger.info('Error - Failed to retrieve options. ' \
                             'Check that app is bound to a Cloudant service.')
            exit(-1)

        Wishlist.logger.info('Cloudant Endpoint: %s', opts['url'])
        try:
            if ADMIN_PARTY:
                Wishlist.logger.info('Running in Admin Party Mode...')
            Wishlist.client = Cloudant(opts['username'],
                                  opts['password'],
                                  url=opts['url'],
                                  connect=True,
                                  auto_renew=True,
                                  admin_party=ADMIN_PARTY
                                 )
        except ConnectionError:
            raise AssertionError('Cloudant service could not be reached')

        # Create database if it doesn't exist
        try:
            Wishlist.database = Wishlist.client[dbname]
        except KeyError:
            # Create a database using an initialized client
            Wishlist.database = Wishlist.client.create_database(dbname)
        # check for success
        if not Wishlist.database.exists():
            raise AssertionError('Database [{}] could not be obtained'.format(dbname))
