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
from unittest.mock import patch, MagicMock
from urllib.parse import quote_plus
from wsgi import app
from service import config  # , routes
from service.common import status
from service.models import init_db, db, Product, DataValidationError
from service.routes import data_reset
from tests.factories import ProductFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/api/products"


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
        api_key = config.API_KEY
        # api_key = routes.generate_apikey()
        app.config["API_KEY"] = api_key
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
        self.headers = {"X-Api-Key": app.config["API_KEY"]}
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        resp = self.client.delete(BASE_URL, headers=self.headers)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
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
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(b"Product Demo REST API Service", response.data)

    # ----------------------------------------------------------
    # TEST LIST
    # ----------------------------------------------------------

    def test_get_product_list(self):
        """It should Get a list of Products"""
        self._create_products(5)
        response = self.client.get(f"{BASE_URL}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), 5)

    # ----------------------------------------------------------
    # TEST CREATE
    # ----------------------------------------------------------
    def test_create_product(self):
        """It should Create a new Product"""
        test_product = ProductFactory()
        logging.debug("Test Product: %s", test_product.serialize())
        response = self.client.post(
            BASE_URL, json=test_product.serialize(), headers=self.headers
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_product = response.get_json()
        self.assertEqual(new_product["name"], test_product.name)
        self.assertEqual(new_product["description"], test_product.description)
        self.assertEqual(new_product["price"], float(test_product.price))

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_product = response.get_json()
        self.assertEqual(new_product["name"], test_product.name)
        self.assertEqual(new_product["description"], test_product.description)
        self.assertEqual(new_product["price"], float(test_product.price))

    # ----------------------------------------------------------
    # TEST READ
    # ----------------------------------------------------------
    def test_get_product(self):
        """It should Get a single Product"""
        # get the id of a product
        test_product = self._create_products(1)[0]
        response = self.client.get(
            f"{BASE_URL}/{test_product.id}", headers=self.headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data["name"], test_product.name)

    def test_get_product_not_found(self):
        """It should not Get a Product thats not found"""
        response = self.client.get(f"{BASE_URL}/0", headers=self.headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    # ----------------------------------------------------------
    # TEST UPDATE
    # ----------------------------------------------------------
    def test_update_product(self):
        """It should Update an existing Product"""
        # create a product to update
        test_product = ProductFactory()
        response = self.client.post(
            BASE_URL, json=test_product.serialize(), headers=self.headers
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the product
        new_product = response.get_json()
        logging.debug(new_product)
        new_product["description"] = "unknown"
        response = self.client.put(
            f"{BASE_URL}/{new_product['id']}", json=new_product, headers=self.headers
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_product = response.get_json()
        self.assertEqual(updated_product["description"], "unknown")

    # ----------------------------------------------------------
    # TEST LIKE
    # ----------------------------------------------------------
    def test_like_product(self):
        """It should Like an existing Product"""
        # create a product to like
        test_product = ProductFactory()
        response = self.client.post(
            BASE_URL, json=test_product.serialize(), headers=self.headers
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # like the product
        new_product = response.get_json()
        logging.debug(new_product)
        response = self.client.put(
            f"{BASE_URL}/{new_product['id']}/like",
            json=new_product,
            headers=self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        liked_product = response.get_json()
        self.assertEqual(liked_product["likes"], 1)

    def test_like_non_existing_product(self):
        """It should return 404 when liking a non-existent product"""
        response = self.client.put(f"{BASE_URL}/99999999/like", headers=self.headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        self.assertIn("was not found", data["message"])

    # ----------------------------------------------------------
    # TEST DELETE
    # ----------------------------------------------------------
    def test_delete_product(self):
        """It should Delete a Product"""
        test_product = self._create_products(1)[0]
        response = self.client.delete(
            f"{BASE_URL}/{test_product.id}", headers=self.headers
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        product = Product.find(test_product.id)
        self.assertIsNone(product)

    def test_delete_non_existing_product(self):
        """It should Delete a Product even if it doesn't exist"""
        response = self.client.delete(f"{BASE_URL}/99999999", headers=self.headers)
        print("RESPONSE STATUS:", response.status_code)
        print("RESPONSE DATA:", response.data.decode())
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)

    def test_remove_all_products(self):
        """It should remove all products from the database"""
        self._create_products(5)
        all_products = Product.all()
        self.assertGreater(len(all_products), 0)
        Product.remove_all()
        all_products = Product.all()
        self.assertEqual(len(all_products), 0)

    # ----------------------------------------------------------
    # TEST QUERY
    # ----------------------------------------------------------

    def test_query_by_name(self):
        """It should Query Products by name"""
        products = self._create_products(5)
        test_name = products[0].name
        name_count = len([product for product in products if product.name == test_name])
        response = self.client.get(BASE_URL, query_string={"name": test_name})
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
            f"{BASE_URL}",
            query_string=f"sku={quote_plus(test_sku)}",
            headers=self.headers,
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
        response = self.client.get(
            f"{BASE_URL}", query_string=f"min_price={min_price}", headers=self.headers
        )
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
        response = self.client.get(
            BASE_URL, query_string=f"max_price={max_price}", headers=self.headers
        )
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
            BASE_URL,
            query_string=f"min_price={min_price}&max_price={max_price}",
            headers=self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(len(data), price_count)
        # Check the data just to be sure
        for product in data:
            self.assertGreaterEqual(float(product["price"]), min_price)
            self.assertLessEqual(float(product["price"]), max_price)


######################################################################
#  T E S T   S A D   P A T H S
######################################################################
class TestSadPaths(TestCase):
    """Test REST Exception Handling"""

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        self.headers = {"X-Api-Key": app.config["API_KEY"]}

    def test_method_not_allowed(self):
        """It should not allow update without a product id"""
        response = self.client.put(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_create_product_no_data(self):
        """It should not Create a Product with missing data"""
        response = self.client.post(BASE_URL, json={}, headers=self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_no_content_type(self):
        """It should not Create a Product with no content type"""
        response = self.client.post(BASE_URL, headers=self.headers)
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_product_wrong_content_type(self):
        """It should not Create a Product with the wrong content type"""
        response = self.client.post(
            BASE_URL, data="hello", content_type="text/html", headers=self.headers
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_product_bad_price(self):
        """It should not Create a Product with bad price data"""
        product = ProductFactory()
        logging.debug(product)
        # change price to a string
        test_product = product.serialize()
        test_product["price"] = "not-a-number"  # invalid price
        response = self.client.post(BASE_URL, json=test_product, headers=self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_duplicate_sku(self):
        """It should not Create a Product with duplicate SKU"""
        # Create a product with a specific SKU
        product1 = ProductFactory()
        product1.create()

        # Try to create another product with the same SKU
        product2 = ProductFactory()
        product2.sku = product1.sku  # Set the same SKU

        # Serialize and try to create
        test_product = product2.serialize()
        response = self.client.post(BASE_URL, json=test_product, headers=self.headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_product_bad_json(self):
        """It should not Create a Product with bad JSON"""
        # Try to create with invalid JSON but correct content type
        response = self.client.post(
            BASE_URL,
            data="this is not valid JSON",
            content_type="application/json",
            headers=self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_product_not_found(self):
        """It should not Update a Product that doesn't exist"""
        # Create a fake product dictionary
        fake_product = {
            "id": 0,
            "name": "fake",
            "description": "fake",
            "price": 10.0,
            "sku": "fake123",
        }
        # Try to update a product that doesn't exist
        response = self.client.put(
            f"{BASE_URL}/0", json=fake_product, headers=self.headers
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_product_no_content_type(self):
        """It should not Update a Product with no content type"""
        # Create a valid product first
        test_product = ProductFactory()
        test_product.create()
        # Try to update without a content type
        response = self.client.put(
            f"{BASE_URL}/{test_product.id}", headers=self.headers
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_update_product_wrong_content_type(self):
        """It should not Update a Product with wrong content type"""
        # Create a valid product first
        test_product = ProductFactory()
        test_product.create()
        # Try to update with the wrong content type
        response = self.client.put(
            f"{BASE_URL}/{test_product.id}",
            data="hello world",
            content_type="text/html",
            headers=self.headers,
        )
        self.assertEqual(response.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    @patch("service.models.Product.find_by_name")
    def test_bad_request(self, bad_request_mock):
        """It should return a Bad Request error from Find By Name"""
        bad_request_mock.side_effect = DataValidationError()
        response = self.client.get(BASE_URL, query_string="name=test")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("service.models.Product.find_by_name")
    def test_mock_search_data(self, product_find_mock):
        """It should show how to mock data"""
        mock_product = MagicMock()
        mock_product.serialize.return_value = {"name": "test_product"}
        product_find_mock.return_value = [mock_product]
        response = self.client.get(BASE_URL, query_string="name=test_product")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(data[0]["name"], "test_product")

    @patch("service.models.Product.query")
    def test_remove_all_products_failure(self, mock_query):
        """It should raise an exception if remove_all() fails"""
        mock_query.delete.side_effect = Exception("DB error")
        with self.assertRaises(Exception) as context:
            Product.remove_all()
        self.assertIn("DB error", str(context.exception))

    @patch("service.routes.Product.remove_all")
    def test_data_reset_calls_remove_all(self, mock_remove_all):
        """It should delegate product clearing to Product.remove_all()"""
        data_reset()
        mock_remove_all.assert_called_once()

    @patch("service.routes.Product.remove_all")
    @patch("service.routes.app.logger.warning")
    def test_delete_all_products_outside_test_mode(self, mock_warning, mock_remove_all):
        """It should log a warning and not delete when not in TESTING mode"""

        app.config["TESTING"] = False

        response = self.client.delete(BASE_URL, headers=self.headers)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        mock_remove_all.assert_not_called()
        mock_warning.assert_called_once_with(
            "Request to clear database while system not under test"
        )

        app.config["TESTING"] = True

    @patch("service.models.db.create_all")
    def test_init_db_calls_create_all(self, mock_create_all):
        """It should call db.create_all when init_db is called"""
        init_db()
        mock_create_all.assert_called_once()
