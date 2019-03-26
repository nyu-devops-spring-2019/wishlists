# Copyright 2016, 2017 John Rofrano. All Rights Reserved.
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
"""
Models for Wishlist Demo Service

All of the models are stored in this module

Models
------
Wishlist - A Wishlist used to save items

Attributes:
-----------
name (string) - the name of the wishlist
customer_id (integer) - the id of the customer
item_id (integer) - id of the item

"""
import logging
from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass

class Wishlist(db.Model):
    """
    Class that represents a Wishlist

    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """
    logger = logging.getLogger(__name__)
    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63))
    customer_id = db.Column(db.Integer)
    item_id = db.Column(db.Integer)

    def __repr__(self):
        return '<Wishlist %r>' % (self.name)

    def save(self):
        """
        Saves a Wishlist to the data store
        """
        if not self.id:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        """ Removes a Wishlist from the data store """
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ Serializes a Wishlistt into a dictionary """
        return {"id": self.id,
                "name": self.name,
                "customer_id": self.customer_id,
                "item_id": self.item_id}

    def deserialize(self, data):
        """
        Deserializes a Wishlist from a dictionary

        Args:
            data (dict): A dictionary containing the Wishlist data
        """
        try:
            self.name = data['name']
            self.customer_id = data['customer_id']
            self.item_id = data['item_id']
        except KeyError as error:
            raise DataValidationError('Invalid wishlist: missing ' + error.args[0])
        except TypeError as error:
            raise DataValidationError('Invalid wishlist: body of request contained' \
                                      'bad or no data')
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        cls.logger.info('Initializing database')
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Wishlists in the database """
        cls.logger.info('Processing all Wishlists')
        return cls.query.all()

    @classmethod
    def find(cls, wishlist_id):
        """ Finds a wishlist by it's ID """
        cls.logger.info('Processing lookup for id %s ...', wishlist_id)
        return cls.query.get(wishlist_id)

    @classmethod
    def find_or_404(cls, wishlist_id):
        """ Find a wishlist by it's id """
        cls.logger.info('Processing lookup or 404 for id %s ...', wishlist_id)
        return cls.query.get_or_404(wishlist_id)

    @classmethod
    def find_by_name(cls, name):
        """ Returns all wishlists with the given name

        Args:
            name (string): the name of the wishlists you want to match
        """
        cls.logger.info('Processing name query for %s ...', name)
        return cls.query.filter(cls.name == name)

    @classmethod
    def find_by_item_id(cls, item_id):
        """ Returns all of the wishlists that contain the item

        Args:
            item_id (integer): the item_id of the wishlists you want to match
        """
        cls.logger.info('Processing item_id query for %s ...', item_id)
        return cls.query.filter(cls.item_id == item_id)

    @classmethod
    def find_by_customer_id(cls, customer_id):
        """ Returns all of the wishlists that contain the customer

        Args:
            customer_id (integer): the customer_id of the wishlists you want to match
        """
        cls.logger.info('Processing customer_id query for %s ...', customer_id)
        return cls.query.filter(cls.customer_id == customer_id)
