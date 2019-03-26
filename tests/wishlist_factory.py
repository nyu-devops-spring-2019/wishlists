"""
Test Factory to make fake objects for testing
"""
import factory
from factory.fuzzy import FuzzyChoice
from app.models import Wishlist

class WishlistFactory(factory.Factory):
    """ Creates fake wishlists """
    class Meta:
        model = Wishlist
    id = factory.Sequence(lambda n: n)
    name = factory.Faker('first_name')
    item_id = FuzzyChoice(choices=[3, 2, 7, 1, 9])
    customer_id = FuzzyChoice(choices=[22, 33, 44, 55])

if __name__ == '__main__':
    for _ in range(10):
        wishlist = WishlistFactory()
        print(wishlist.serialize())
