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
Product Service with Swagger

Paths:
------
GET / - Displays a UI for Selenium testing
GET /products - Returns a list all of the Products
GET /products/{id} - Returns the Product with a given id number
POST /products - creates a new Product record in the database
PUT /products/{id} - updates a Product record in the database
DELETE /products/{id} - deletes a Product record in the database
"""

import secrets

# from functools import wraps
# from flask import request
from flask import current_app as app  # Import Flask application
from flask_restx import Api, Resource, fields, reqparse
from service.models import Product
from service.common import status  # HTTP Status Codes

# Document the type of authorization required
authorizations = {"apikey": {"type": "apiKey", "in": "header", "name": "X-Api-Key"}}

######################################################################
# Configure Swagger before initializing it
######################################################################
api = Api(
    app,
    version="1.0.0",
    title="Product REST API Service",
    description="This is a sample Product server.",
    default="products",
    default_label="Product operations",
    doc="/apidocs",  # default also could use doc='/apidocs/'
    authorizations=authorizations,
    prefix="/api",
)


######################################################################
# Configure the Root route before OpenAPI
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return app.send_static_file("index.html")


# Define the model so that the docs reflect what can be sent
create_model = api.model(
    "Product",
    {
        "name": fields.String(
            required=True,
            description="The name of the Product",
            example="Wireless Mouse",
        ),
        "sku": fields.String(
            required=True, description="The SKU of the Product", example="SKU12345"
        ),
        "description": fields.String(
            required=False,
            description="The description of the Product",
            example="A sleek wireless mouse with ergonomic design",
        ),
        "price": fields.Float(
            required=True, description="The price of the Product", example=49.99
        ),
        "image_url": fields.String(
            required=False,
            description="URL to the product image",
            example="https://example.com/images/mouse.png",
        ),
    },
)


product_model = api.inherit(
    "ProductModel",
    create_model,
    {
        "id": fields.Integer(
            readOnly=True,
            description="The unique id assigned internally by the service",
            example=1,
        ),
        "likes": fields.Integer(
            readOnly=True, description="The number of likes for this product", example=7
        ),
        "created_time": fields.DateTime(
            readOnly=True,
            description="The time when this product was created",
            example="2024-04-20T14:35:22.123Z",
        ),
        "updated_time": fields.DateTime(
            readOnly=True,
            description="The time when this product was last updated",
            example="2024-04-21T16:10:45.456Z",
        ),
    },
)

# query string arguments
product_args = reqparse.RequestParser()
product_args.add_argument(
    "name", type=str, location="args", required=False, help="List Products by name"
)
product_args.add_argument(
    "sku", type=str, location="args", required=False, help="List Products by SKU"
)
product_args.add_argument(
    "min_price",
    type=float,
    location="args",
    required=False,
    help="List Products with price greater than or equal to this value",
)
product_args.add_argument(
    "max_price",
    type=float,
    location="args",
    required=False,
    help="List Products with price less than or equal to this value",
)


######################################################################
# Authorization Decorator
######################################################################
# def token_required(func):
#     """Decorator to require a token for this endpoint"""

#     @wraps(func)
#     def decorated(*args, **kwargs):
#         token = None
#         if "X-Api-Key" in request.headers:
#             token = request.headers["X-Api-Key"]

#         if app.config.get("API_KEY") and app.config["API_KEY"] == token:
#             return func(*args, **kwargs)

#         return {"message": "Invalid or missing token"}, 401

#     return decorated


######################################################################
# Function to generate a random API key (good for testing)
######################################################################
def generate_apikey():
    """Helper function used when testing API keys"""
    return secrets.token_hex(16)


######################################################################
#  PATH: /health
######################################################################
@api.route("/health")
class HealthResource(Resource):
    """Health Status"""

    @api.doc("get_health")
    def get(self):
        """Health Status"""
        return {"status": "OK"}, status.HTTP_200_OK


######################################################################
#  PATH: /products/{id}
######################################################################
@api.route("/products/<int:product_id>")
@api.param("product_id", "The Product identifier")
class ProductResource(Resource):
    """
    ProductResource class

    Allows the manipulation of a single Product
    GET /products/{id} - Returns a Product with the id
    PUT /products/{id} - Update a Product with the id
    DELETE /products/{id} -  Deletes a Product with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE A PRODUCT
    # ------------------------------------------------------------------
    @api.doc("get_products")
    @api.response(404, "Product not found")
    @api.marshal_with(product_model)
    def get(self, product_id):
        """
        Retrieve a single Product

        This endpoint will return a Product based on it's id
        """
        app.logger.info("Request to Retrieve a product with id [%s]", product_id)
        product = Product.find(product_id)
        if not product:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Product with id '{product_id}' was not found.",
            )
        return product.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING PRODUCT
    # ------------------------------------------------------------------
    @api.doc("update_products", security="apikey")
    @api.response(404, "Product not found")
    @api.response(400, "The posted Product data was not valid")
    @api.expect(product_model)
    @api.marshal_with(product_model)
    # @token_required
    def put(self, product_id):
        """
        Update a Product

        This endpoint will update a Product based the body that is posted
        """
        app.logger.info("Request to Update a product with id [%s]", product_id)
        product = Product.find(product_id)
        if not product:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Product with id '{product_id}' was not found.",
            )
        app.logger.debug("Payload = %s", api.payload)
        product.deserialize(api.payload)
        product.id = product_id
        product.update()
        return product.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A PRODUCT
    # ------------------------------------------------------------------
    @api.doc("delete_products", security="apikey")
    @api.response(204, "Product deleted")
    # @token_required
    def delete(self, product_id):
        """
        Delete a Product

        This endpoint will delete a Product based the id specified in the path
        """
        app.logger.warning(">>> [DELETE HIT] Reached delete() for id: %s", product_id)
        product = Product.find(product_id)
        if product:
            product.delete()
            app.logger.info("Product with id [%s] was deleted", product_id)

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /products
######################################################################
@api.route("/products", strict_slashes=False)
class ProductCollection(Resource):
    """Handles all interactions with collections of Products"""

    # ------------------------------------------------------------------
    # LIST ALL PRODUCTS
    # ------------------------------------------------------------------
    @api.doc("list_products")
    @api.expect(product_args, validate=True)
    def get(self):
        """
        List all Products

        This endpoint allows you to retrieve products from the database.
        You can optionally filter the results by name, SKU, min_price, and/or max_price.
        """
        app.logger.info("Request for product list")
        products = []
        args = product_args.parse_args()

        if args["sku"]:
            products = Product.find_by_sku(args["sku"])
        elif args["name"]:
            products = Product.find_by_name(args["name"])
        elif args["min_price"] and args["max_price"]:
            products = Product.find_by_price_range(
                float(args["min_price"]), float(args["max_price"])
            )
        elif args["min_price"]:
            products = Product.find_by_min_price(float(args["min_price"]))
        elif args["max_price"]:
            products = Product.find_by_max_price(float(args["max_price"]))
        else:
            products = Product.all()

        results = [product.serialize() for product in products]
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW PRODUCT
    # ------------------------------------------------------------------
    @api.doc("create_products", security="apikey")
    @api.response(400, "The posted data was not valid")
    @api.expect(create_model)
    @api.marshal_with(product_model, code=201)
    # @token_required
    def post(self):
        """
        Creates a Product
        This endpoint will create a Product based the data in the body that is posted
        """
        app.logger.info("Request to Create a Product")
        product = Product()
        app.logger.debug("Payload = %s", api.payload)
        product.deserialize(api.payload)
        product.create()
        app.logger.info("Product with new id [%s] created!", product.id)
        location_url = api.url_for(
            ProductResource, product_id=product.id, _external=True
        )
        return product.serialize(), status.HTTP_201_CREATED, {"Location": location_url}

    # ------------------------------------------------------------------
    # DELETE ALL PRODUCTS (for testing only)
    # ------------------------------------------------------------------
    @api.doc("delete_all_products", security="apikey")
    @api.response(204, "All Products deleted")
    # @token_required
    def delete(self):
        """
        Delete all Product
        This endpoint will delete all Product only if the system is under test
        """
        app.logger.info("Request to Delete all products...")
        if "TESTING" in app.config and app.config["TESTING"]:
            Product.remove_all()
            app.logger.info("Removed all Products from the database")
        else:
            app.logger.warning("Request to clear database while system not under test")
        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /products/{id}/like
######################################################################
@api.route("/products/<int:product_id>/like")
@api.param("product_id", "The Product identifier")
class LikeResource(Resource):
    """Like actions on a Product"""

    @api.doc("like_products")
    @api.response(404, "Product not found")
    @api.response(409, "The Product cannot be liked")
    @api.marshal_with(product_model)
    def put(self, product_id):
        """
        Like a Product

        This endpoint will increment the like count for a Product
        """
        app.logger.info("Request to Like a product with id [%s]", product_id)
        product = Product.find(product_id)
        if not product:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Product with id '{product_id}' was not found.",
            )

        product.likes += 1
        product.update()
        app.logger.info("Product with id [%s] has been liked!", product.id)
        return product.serialize(), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def abort(error_code: int, message: str):
    """Logs errors before aborting"""
    app.logger.error(message)
    api.abort(error_code, message)


def data_reset():
    """Removes all Products from the database"""
    Product.remove_all()
