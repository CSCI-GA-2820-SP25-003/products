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

    description = FuzzyChoice(
        choices=[
            "Product 1 description",
            "Product 2 description",
            "Product 3 description",
            "Product 4 description",
            "Product 5 description",
        ]
    )
    image_url = FuzzyChoice(
        choices=[
            "https://t4.ftcdn.net/jpg/01/36/70/67/360_F_136706734_KWhNBhLvY5XTlZVocpxFQK1FfKNOYbMj.jpg",
            "https://www.ikea.com/us/en/images/products/blahaj-soft-toy-shark__0710175_pe727378_s5.jpg",
            "https://i.ebayimg.com/images/g/NIkAAOSwXSVhZDSc/s-l1200.jpg",
        ]
    )
    likes = 0
    price = FuzzyDecimal(10.00, 500.00, precision=2)
