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
Product Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Product
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Product
from service.common import status  # HTTP Status Codes


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

# Todo: Place your REST API code here ...


######################################################################
# LIST ALL PRODUCTS
######################################################################
@app.route("/products", methods=["GET"])
def list_products():
    """Returns all of the Products"""
    app.logger.info("Request for product list")

    products = []

    # Parse any arguments from the query string
    name = request.args.get("name")
    sku = request.args.get("sku")
    min_price = request.args.get("min_price")
    max_price = request.args.get("max_price")

    if sku:
        app.logger.info("Find by sku: %s", sku)
        products = Product.find_by_sku(sku)
    elif name:
        app.logger.info("Find by name: %s", name)
        products = Product.find_by_name(name)
    elif min_price and max_price:
        app.logger.info("Find by price range: %s - %s", min_price, max_price)
        products = Product.find_by_price_range(float(min_price), float(max_price))
    elif min_price:
        app.logger.info("Find by min price: %s", min_price)
        products = Product.find_by_min_price(float(min_price))
    elif max_price:
        app.logger.info("Find by max price: %s", max_price)
        products = Product.find_by_max_price(float(max_price))
    else:
        app.logger.info("Find all")
        products = Product.all()

    results = [product.serialize() for product in products]
    app.logger.info("Returning %d products", len(results))
    return jsonify(results), status.HTTP_200_OK
