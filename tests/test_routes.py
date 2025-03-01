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
TestProduct API Service Test Suite
"""

# pylint: disable=duplicate-code
import os
import logging
from unittest import TestCase
from urllib.parse import quote_plus
from wsgi import app
from service.common import status
from service.models import db, Product
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestYourResourceService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    # Utility functions
    ######################################################################
    def _create_products(self, count: int = 1) -> list:
        """Factory method to create products in bulk"""
        products = []
        for _ in range(count):
            test_product = ProductFactory()
            test_product.create()
            products.append(test_product)
        return products

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    # Todo: Add your test cases here...

    # ----------------------------------------------------------
    # TEST LIST
    # ----------------------------------------------------------

    def test_get_product_list(self):
        """It should Get a list of Products"""
        self._create_products(5)
        response = self.client.get("/products")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    # ----------------------------------------------------------
    # TEST READ
    # ----------------------------------------------------------
    def test_get_product(self):
        """It should Get a single Product"""
        # get the id of a product
        test_product = self._create_products(1)[0]
        response = self.client.get(f"/products/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_product.name)

    def test_get_product_not_found(self):
        """It should not Get a Product thats not found"""
        response = self.client.get("/products/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    # ----------------------------------------------------------
    # TEST DELETE
    # ----------------------------------------------------------
    def test_delete_product(self):
        """It should Delete a Product"""
        test_product = self._create_products(1)[0]
        response = self.client.delete(f"/products/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"/products/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_non_existing_product(self):
        """It should Delete a Product even if it doesn't exist"""
        response = self.client.delete("/products/0")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

    # ----------------------------------------------------------
    # TEST QUERY
    # ----------------------------------------------------------

    def test_query_by_name(self):
        """It should Query Products by name"""
        products = self._create_products(5)
        test_name = products[0].name
        name_count = len([product for product in products if product.name == test_name])
        response = self.client.get(
            "/products", query_string=f"name={quote_plus(test_name)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), name_count)
        # Check the data just to be sure
        for product in data:
            self.assertEqual(product["name"], test_name)

    def test_query_by_sku(self):
        """It should Query Products by SKU"""
        products = self._create_products(5)
        test_sku = products[0].sku
        # Since SKU is unique, we expect only one result
        response = self.client.get(
            "/products", query_string=f"sku={quote_plus(test_sku)}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 1)
        # Check the data just to be sure
        self.assertEqual(data[0]["sku"], test_sku)

    def test_query_by_min_price(self):
        """It should Query Products by minimum price"""
        products = self._create_products(10)
        min_price = 50.0
        price_count = len(
            [product for product in products if float(product.price) >= min_price]
        )
        response = self.client.get("/products", query_string=f"min_price={min_price}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), price_count)
        # Check the data just to be sure
        for product in data:
            self.assertGreaterEqual(float(product["price"]), min_price)

    def test_query_by_max_price(self):
        """It should Query Products by maximum price"""
        products = self._create_products(10)
        max_price = 100.0
        price_count = len(
            [product for product in products if float(product.price) <= max_price]
        )
        response = self.client.get("/products", query_string=f"max_price={max_price}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), price_count)
        # Check the data just to be sure
        for product in data:
            self.assertLessEqual(float(product["price"]), max_price)

    def test_query_by_price_range(self):
        """It should Query Products by price range"""
        products = self._create_products(10)
        min_price = 50.0
        max_price = 100.0
        price_count = len(
            [
                product
                for product in products
                if min_price <= float(product.price) <= max_price
            ]
        )
        response = self.client.get(
            "/products", query_string=f"min_price={min_price}&max_price={max_price}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), price_count)
        # Check the data just to be sure
        for product in data:
            self.assertGreaterEqual(float(product["price"]), min_price)
            self.assertLessEqual(float(product["price"]), max_price)
