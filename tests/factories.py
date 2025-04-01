"""
Test Factory to make fake objects for testing
"""

# from datetime import date
import factory
from factory.fuzzy import FuzzyChoice, FuzzyText, FuzzyDecimal
from service.models import Product


class ProductFactory(factory.Factory):
    """Creates fake pets that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Product

    id = factory.Sequence(lambda n: n)
    sku = FuzzyText(length=62)
    name = FuzzyChoice(
        choices=["E-Reader", "Vacuum Cleaner", "Jeans", "Potato Chips", "Calculator"]
    )

    description = FuzzyText(length=256)
    image_url = FuzzyChoice(choices=["https://www.google.com", "https://www.nyu.edu"])
    likes = 0
    price = FuzzyDecimal(10.00, 500.00, precision=2)
