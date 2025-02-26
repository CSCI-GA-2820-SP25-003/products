######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
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
######################################################################

"""
Test cases for Pet Model
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from wsgi import app
from service.models import Product, DataValidationError, db
from .factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  B A S E   T E S T   C A S E S
######################################################################
class TestCaseBase(TestCase):
    """Base Test Case for common setup"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
class TestProductModel(TestCaseBase):
    """Product Model CRUD Tests"""

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(
            sku="TEST01",
            name="Test1",
            description="Test Description 1",
            price=123.21,
            image_url="http://www.nyu.edu",
        )
        self.assertEqual(str(product), "<Product Test1 id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.sku, "TEST01")
        self.assertEqual(product.name, "Test1")
        self.assertEqual(product.description, "Test Description 1")
        self.assertEqual(float(product.price), 123.21)
        self.assertEqual(product.image_url, "http://www.nyu.edu")

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = Product(
            sku="TEST02", name="Test2", description="Test Description 2", price=321.23
        )
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)

    def test_read_a_product(self):
        """It should Read a Product"""
        product = ProductFactory()
        logging.debug(product)
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # Fetch it back
        found_product = Product.find(product.id)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.sku, product.sku)
        self.assertEqual(found_product.price, product.price)
        self.assertEqual(found_product.description, product.description)

    def test_update_a_product(self):
        """It should Update a Product"""
        product = ProductFactory()
        logging.debug(product)
        product.id = None
        product.create()
        logging.debug(product)
        self.assertIsNotNone(product.id)
        # Change it and save it
        product.description = "testing"
        original_id = product.id
        product.update()
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, "testing")
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        products = Product.all()
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].id, original_id)
        self.assertEqual(products[0].description, "testing")

    def test_update_no_id(self):
        """It should not Update a Product with no id"""
        product = ProductFactory()
        logging.debug(product)
        product.id = None
        self.assertRaises(DataValidationError, product.update)

    def test_delete_a_product(self):
        """It should Delete a Product"""
        product = ProductFactory()
        product.create()
        self.assertEqual(len(Product.all()), 1)
        # delete the product and make sure it isn't in the database
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """It should List all Products in the database"""
        products = Product.all()
        self.assertEqual(products, [])
        # Create 5 Products
        for _ in range(5):
            product = ProductFactory()
            product.create()
        # See if we get back 5 products
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_serialize_a_product(self):
        """It should serialize a Product"""
        product = ProductFactory()
        data = product.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], product.id)
        self.assertIn("name", data)
        self.assertEqual(data["name"], product.name)
        self.assertIn("sku", data)
        self.assertEqual(data["sku"], product.sku)
        self.assertIn("description", data)
        self.assertEqual(data["description"], product.description)
        self.assertIn("price", data)
        self.assertEqual(float(data["price"]), float(product.price))
        self.assertIn("image_url", data)
        self.assertEqual(data["image_url"], product.image_url)

    def test_deserialize_a_product(self):
        """It should de-serialize a Product"""
        data = ProductFactory().serialize()
        product = Product()
        product.deserialize(data)
        self.assertNotEqual(product, None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, data["name"])
        self.assertEqual(product.sku, data["sku"])
        self.assertEqual(product.description, data["description"])
        self.assertEqual(float(product.price), float(data["price"]))
        self.assertEqual(product.image_url, data["image_url"])

    def test_deserialize_missing_data(self):
        """It should not deserialize a Product with missing data"""
        data = {"id": 1, "name": "Product1", "sku": "SKU1"}
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        data = "this is not a dictionary"
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_bad_price(self):
        """It should not deserialize a bad price attribute"""
        test_product = ProductFactory()
        data = test_product.serialize()
        data["price"] = "bad price"
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)


# ######################################################################
# #  T E S T   E X C E P T I O N   H A N D L E R S
# ######################################################################
# class TestExceptionHandlers(TestCaseBase):
#     """Product Model Exception Handlers"""

#     @patch("service.models.db.session.commit")
#     def test_create_exception(self, exception_mock):
#         """It should catch a create exception"""
#         exception_mock.side_effect = Exception()
#         product = ProductFactory()
#         self.assertRaises(DataValidationError, product.create)

#     @patch("service.models.db.session.commit")
#     def test_update_exception(self, exception_mock):
#         """It should catch a update exception"""
#         exception_mock.side_effect = Exception()
#         product = ProductFactory()
#         self.assertRaises(DataValidationError, product.update)

#     @patch("service.models.db.session.commit")
#     def test_delete_exception(self, exception_mock):
#         """It should catch a delete exception"""
#         exception_mock.side_effect = Exception()
#         product = ProductFactory()
#         self.assertRaises(DataValidationError, product.delete)


######################################################################
#  Q U E R Y   T E S T   C A S E S
######################################################################
class TestModelQueries(TestCaseBase):
    """Product Model Query Tests"""

    def test_find_product(self):
        """It should Find a Product by ID"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        logging.debug(products)
        # make sure they got saved
        self.assertEqual(len(Product.all()), 5)
        # find the 2nd product in the list
        product = Product.find(products[1].id)
        self.assertIsNot(product, None)
        self.assertEqual(product.id, products[1].id)
        self.assertEqual(product.name, products[1].name)
        self.assertEqual(product.sku, products[1].sku)
        self.assertEqual(product.price, products[1].price)
        self.assertEqual(product.description, products[1].description)

    def test_find_by_sku(self):
        """It should Find a Product by SKU"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        sku = products[0].sku
        # Since SKU is unique, there should be only 1 match
        found = Product.find_by_sku(sku)
        self.assertEqual(found.count(), 1)
        self.assertEqual(found.first().sku, sku)

    def test_find_by_name(self):
        """It should Find Products by Name"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        name = products[0].name
        count = len([product for product in products if product.name == name])
        found = Product.find_by_name(name)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.name, name)

    def test_find_by_price_range(self):
        """It should Find Products by Price Range"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        min_price = 50.0
        max_price = 150.0
        count = len(
            [product for product in products if min_price <= product.price <= max_price]
        )
        found = Product.find_by_price_range(min_price, max_price)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertGreaterEqual(product.price, min_price)
            self.assertLessEqual(product.price, max_price)

    def test_find_by_min_price(self):
        """It should Find Products with price greater than or equal to min_price"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        min_price = 75.0
        count = len([product for product in products if product.price >= min_price])
        found = Product.find_by_min_price(min_price)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertGreaterEqual(product.price, min_price)

    def test_find_by_max_price(self):
        """It should Find Products with price less than or equal to max_price"""
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        max_price = 125.0
        count = len([product for product in products if product.price <= max_price])
        found = Product.find_by_max_price(max_price)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertLessEqual(product.price, max_price)
