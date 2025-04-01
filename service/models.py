"""
Models for Product

All of the models are stored in this module
"""

import os
import logging
from decimal import Decimal, InvalidOperation
from flask_sqlalchemy import SQLAlchemy
from retry import retry

# global variables for retry (must be int)
RETRY_COUNT = int(os.environ.get("RETRY_COUNT", 5))
RETRY_DELAY = int(os.environ.get("RETRY_DELAY", 1))
RETRY_BACKOFF = int(os.environ.get("RETRY_BACKOFF", 2))

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


@retry(
    Exception,
    delay=RETRY_DELAY,
    backoff=RETRY_BACKOFF,
    tries=RETRY_COUNT,
    logger=logger,
)
def init_db() -> None:
    """Initialize Tables"""
    db.create_all()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing"""


class Product(db.Model):
    """
    Class that represents a Product
    """

    ##################################################
    # Table Schema
    ##################################################

    id = db.Column(db.Integer, primary_key=True)
    sku = db.Column(db.String(63), unique=True, nullable=False)
    name = db.Column(db.String(63), nullable=False)
    description = db.Column(db.String(256))
    price = db.Column(db.Numeric(10, 2), nullable=False)
    # stock = db.Column(db.Integer, nullable=False, default=0)
    # available = db.Column(db.Boolean(), nullable=False, default=True)
    image_url = db.Column(db.String(256))
    created_time = db.Column(db.DateTime, nullable=False, default=db.func.now())
    # need test or delete for the updated_at
    updated_time = db.Column(
        db.DateTime, nullable=False, default=db.func.now(), onupdate=db.func.now()
    )
    likes = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<Product {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a Product to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a Product to the database
        """
        if not self.id:
            raise DataValidationError("Update called with empty ID field")

        try:
            db.session.commit()
        except Exception as error:
            db.session.rollback()
            raise DataValidationError("Error updating record: " + str(error)) from error

    def delete(self):
        """Removes a Product from the data store"""
        logger.info("Deleting %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def serialize(self) -> dict:
        """Serializes a Product into a dictionary"""
        return {
            "id": self.id,
            "sku": self.sku,
            "name": self.name,
            "description": self.description,
            "price": str(self.price),
            "image_url": self.image_url,
            "likes": self.likes,
            "created_time": (
                self.created_time.isoformat() if self.created_time else None
            ),
            "updated_time": (
                self.updated_time.isoformat() if self.updated_time else None
            ),
        }

    def deserialize(self, data: dict):
        """
        Deserializes a Product from a dictionary

        Args:
            data (dict): A dictionary containing the Product data
        """
        try:
            self.sku = data["sku"]
            self.name = data["name"]
            self.description = data.get("description")
            self.image_url = data.get("image_url")

            if "price" in data:
                try:
                    self.price = Decimal(data["price"])
                except (ValueError, TypeError, InvalidOperation) as error:
                    raise DataValidationError(
                        "Invalid type for decimal [price]: " + str(type(data["price"]))
                    ) from error
            else:
                raise KeyError("price")

        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid product: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid product: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls) -> list:
        """Returns all of the Products in the database"""
        logger.info("Processing all Products")
        return cls.query.all()

    @classmethod
    def find(cls, product_id: int):
        """Finds a Product by its ID

        :param product_id: the id of the Product to find
        :type product_id: int

        :return: an instance with the product_id, or None if not found
        :rtype: Product

        """
        logger.info("Processing lookup for id %s ...", product_id)
        return cls.query.session.get(cls, product_id)

    @classmethod
    def find_by_name(cls, name: str) -> list:
        """Returns all Products with the given name

        :param name: the name of the Products you want to match
        :type name: str

        :return: a collection of Products with that name
        :rtype: list

        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)

    @classmethod
    def find_by_sku(cls, sku: str) -> list:
        """Returns all Products with the given SKU

        :param sku: the SKU of the Product you want to match
        :type sku: str

        :return: a collection of Products with that SKU (should be only one since SKU is unique)
        :rtype: list

        """
        logger.info("Processing SKU query for %s ...", sku)
        return cls.query.filter(cls.sku == sku)

    @classmethod
    def find_by_price_range(cls, min_price: float, max_price: float) -> list:
        """Returns all Products within the given price range

        :param min_price: the minimum price
        :type min_price: float

        :param max_price: the maximum price
        :type max_price: float

        :return: a collection of Products within the price range
        :rtype: list

        """
        logger.info(
            "Processing price range query from %s to %s ...", min_price, max_price
        )
        return cls.query.filter(cls.price >= min_price).filter(cls.price <= max_price)

    @classmethod
    def find_by_min_price(cls, min_price: float) -> list:
        """Returns all Products with price greater than or equal to min_price

        :param min_price: the minimum price
        :type min_price: float

        :return: a collection of Products with price >= min_price
        :rtype: list

        """
        logger.info("Processing minimum price query for %s ...", min_price)
        return cls.query.filter(cls.price >= min_price)

    @classmethod
    def find_by_max_price(cls, max_price: float) -> list:
        """Returns all Products with price less than or equal to max_price

        :param max_price: the maximum price
        :type max_price: float

        :return: a collection of Products with price <= max_price
        :rtype: list

        """
        logger.info("Processing maximum price query for %s ...", max_price)
        return cls.query.filter(cls.price <= max_price)
