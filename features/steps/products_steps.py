"""
Product Steps
Steps file for products.feature
"""

import requests
from compare3 import expect
from behave import given  # pylint: disable=no-name-in-module

# HTTP Return Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
WAIT_TIMEOUT = 60


@given("the following products")
def step_impl(context):
    """Delete all Products and load new ones"""
    # Get a list all of the products
    rest_endpoint = f"{context.base_url}/products"
    context.resp = requests.get(rest_endpoint, timeout=WAIT_TIMEOUT)
    expect(context.resp.status_code).equal_to(HTTP_200_OK)

    # and delete them one by one
    for product in context.resp.json():
        context.resp = requests.delete(
            f"{rest_endpoint}/{product['id']}", timeout=WAIT_TIMEOUT
        )
        expect(context.resp.status_code).equal_to(HTTP_204_NO_CONTENT)

    # load the database with new products
    for row in context.table:
        payload = {
            "name": row["name"],
            "sku": row["sku"],
            "description": row["description"],
            "price": float(row["price"]),
            "image_url": row["image_url"],
            "likes": int(row["likes"]) if "likes" in row else 0,
        }
        context.resp = requests.post(rest_endpoint, json=payload, timeout=WAIT_TIMEOUT)
        expect(context.resp.status_code).equal_to(HTTP_201_CREATED)
