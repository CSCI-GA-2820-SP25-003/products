"""
Models for Product

All of the models are stored in this module
"""

import os
import logging
from flask_sqlalchemy import SQLAlchemy
from decimal import Decimal
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

    # Todo: Place the rest of your schema here...

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
        logger.info("Saving %s", self.name)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

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

    def serialize(self):
        """Serializes a Product into a dictionary"""
        return {
            "id": self.id,
            "sku": self.sku,
            "name": self.name,
            "description": self.description,
            "price": str(self.price),
            "image_url": self.image_url,
            "created_time": self.created_time.isoformat(),
            "updated_time": self.updated_time.isoformat(),
        }

    def deserialize(self, data):
        """
        Deserializes a Product from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.sku = data["sku"]  # SKU is required
            self.name = data["name"]
            self.description = data.get("description")
            self.image_url = data.get("image_url")
            if "price" in data:
                self.price = Decimal(data["price"])
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Product: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Product: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Products in the database"""
        logger.info("Processing all Products")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Product by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.session.get(cls, by_id)

    @classmethod
    def find_by_name(cls, name):
        """Returns all Products with the given name

        Args:
            name (string): the name of the Products you want to match
        """
        logger.info("Processing name query for %s ...", name)
        return cls.query.filter(cls.name == name)
