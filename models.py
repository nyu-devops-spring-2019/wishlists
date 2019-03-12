import os
import json
import logging
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


######################################################################
# Custom Exceptions
######################################################################
class DataValidationError(ValueError):
    pass

######################################################################
# Items Model for database
######################################################################

class Item(db.Model):
    """ Model for an Item """
    logger = logging.getLogger(__name__)
    app = None

    __tablename__ = "items"
    item_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    wishlist_id = db.Column(db.Integer, db.ForeignKey('Wishlist.wishlist_id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    item_name = db.Column(db.String(63), nullable=False)
    item_description = db.Column(db.String(100))

    def __repr__(self):
        return '<Item %r>' % (self.item_name)

    def save(self):
        """ Saves an Item to the database """
        if not self.item_id:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        """ Deletes an Item from the database """
        if self.item_id:
            db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """
        Serializes an Item into a dictionary
        Returns:
            dict
        """
        return {
                "Item_id": self.item_id,
                "wishlist_id": self.wishlist_id,
                "product_id": self.product_id,
                "item_name": self.item_name,
                "Item_description": self.item_description
                }

    def deserialize(self, data, wishlist_id):
        """
        Deserializes an Item from a dictionary
        Args:
            data (dict): A dictionary containing the Item data
        Returns:
            self: instance of Item
        Raises:
            DataValidationError: when bad or missing data
        """
        try:
            self.wishlist_id = wishlist_id
            self.product_id = data['product_id']
            self.item_name = data['item_name']
            self.item_description = data['item_description']

        except KeyError as error:
            raise DataValidationError('Invalid item: missing ' + error.args[0])
        except TypeError as error:
            raise DataValidationError('Invalid item: body of request contained ' \
                                      'bad or no data')
        return self

    @staticmethod
    def init_db(app):
        """ Initializes the database session """
        Item.logger.info('Initializing database')
        Item.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @staticmethod
    def all():
        """
        Fetch all of the Items in the database
        Returns:
            List: list of Items
        """
        Item.logger.info('Processing all Items')
        return Item.query.all()

    @staticmethod
    def get(item_id):
        """
        Get an Item by id
        Args:
            item_id: primary key of items
        Returns:
            Item: item with associated id
        """
        Item.logger.info('Processing lookup for id %s ...', item_id)
        return Item.query.get(item_id)

    @staticmethod
    def find_by_name(name):
        """ Return all Items with the given name
        Args:
            name (string): the name of the Items you want to match
        """
        Item.logger.info('Processing name query for %s ...', name)
        return Item.query.filter(Item.item_name == name)

    @staticmethod
    def find_by_wishlist_id(wishlist_id):
        """ Returns all Items with the given wishlist_id
        Args:
            wishlist_id (integer): the wishlist_id associated with a list of items
        """
        Item.logger.info('Processing wishlist_id query for %s ...', wishlist_id)
        return Item.query.filter(Item.wishlist_id == wishlist_id)


######################################################################
# Wishlist Model for database
######################################################################
class Wishlist(db.Model):
    """A single wishlist"""
    logger = logging.getLogger(__name__)

    __tablename__ = "Wishlist"
    # Table Schema
    wishlist_id = db.Column(db.Integer, primary_key=True)
    wishlist_name = db.Column(db.String(63))
    wishlist_description= db.Column(db.String(63))
    wishlist_available = db.Column(db.Boolean())
    wishlist_customer_id = db.Column(db.Integer)

    def __repr__(self):
        return '<Wishlist %r>' % (self.name)

    def save(self):
        """ Saves an existing wishlist in the database """
        # if the id is None it hasn't been added to the database
        if not self.id:
            db.session.add(self)
        db.session.commit()

    def delete(self):
        """ Deletes a Wishlist from the database """
        db.session.delete(self)
        db.session.commit()

    def serialize(self):
        """ serializes a Wishlist into a dictionary """
        return {"wishlist_id": self.wishlist_id,
                "wishlist_name": self.wishlist_name,
                "wishlist_description": self.wishlist_description,
                "wishlist_available": self.wishlist_available,
                "wishlist_customer_id": self.wishlist_customer_id}

    def deserialize(self, data):
        """ deserializes a Wishlist my marshalling the data """
        try:
            self.wishlist_name = data['wishlist_name']
            self.wishlist_description = data['wishlist_description']
            self.wishlist_available = data['wishlist_available']
            self.wishlist_customer_id = data['wishlist_customer_id']

        except KeyError as error:
            raise DataValidationError('Invalid Wishlist: missing ' + error.args[0])
        except TypeError as error:
            raise DataValidationError('Invalid Wishlist: body of request contained' \
                                      'bad or no data')
        return self

    @staticmethod
    def init_db():
        """ Initializes the database session """
        Wishlist.logger.info('Initializing database')
	# Wishlist.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        # db.init_app(app)
        # app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @staticmethod
    def all():
        """ Return all of the Wishlists in the database """
        Wishlist.logger.info('Processing all Wishlists')
        return Wishlist.query.all()

    @staticmethod
    def all_sorted():
        """ Return all of the Wishlists in the database """
        Wishlist.logger.info('Processing all Wishlists')
        return Wishlist.query.order_by(Wishlist.wishlist_name.desc()).all()

    @staticmethod
    def get(wishlist_id):
        """ Find a Wishlist by it's id """
        Wishlist.logger.info('Processing lookup for id %s ...', wishlist_id)
        return Wishlist.query.get(wishlist_id)

    @staticmethod
    def get_or_404(wishlist_id):
        """ Find a Wishlist by it's id """
        Wishlist.logger.info('Processing lookup or 404 for id %s ...', wishlist_id)
        return Wishlist.query.get_or_404(wishlist_id)

    @staticmethod
    def find_by_name(wishlist_name):
        """ Query that finds Wishlists by their name """
        Wishlist.logger.info('Processing name query for %s ...', wishlist_name)
        return Wishlist.query.filter(Wishlist.wishlist_name == wishlist_name)

    @staticmethod
    def clear_db():
        """Clear database"""
        # Item.query.delete()
        # db.session.commit()
        # Wishlist.query.delete()
        # db.session.commit()
        meta = db.metadata
        for table in reversed(meta.sorted_tables):
            db.session.execute(table.delete())
            db.session.commit()
        #using bluemix and postgresql
        if 'VCAP_SERVICES' in os.environ:
            db.session.execute("ALTER SEQUENCE items_id_seq RESTART with 1;")
            db.session.execute("ALTER SEQUENCE wishlists_id_seq RESTART with 1;")
            db.session.commit()