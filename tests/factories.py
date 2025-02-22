"""
Test Factory to make fake objects for testing
"""

from datetime import date
import factory
from service.models import Product
from factory.fuzzy import FuzzyChoice, FuzzyText, FuzzyDecimal, FuzzyDate


class ProductFactory(factory.Factory):
    """Creates fake pets that you don't have to feed"""

    class Meta:  # pylint: disable=too-few-public-methods
        """Maps factory to data model"""

        model = Product

    id = factory.Sequence(lambda n: n)
    name = FuzzyChoice(
        choices=["E-Reader", "Vacuum Cleaner", "Jeans", "Potato Chips", "Calculator"]
    )

    # Todo: Add your other attributes here...

    description = FuzzyText(length=256)
    price = FuzzyDecimal(10.00, 500.00, precision=2)
    created_time = FuzzyDate(date(2008, 1, 1))
    updated_time = FuzzyDate(date(2008, 1, 1))
