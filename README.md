# NYU Devops Products Service

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

## Overview

This service provides a RESTful API for the Products database to store and manage product information. The service source code is contained in the `/service` directory and related test functions are in the `/tests` directory. The service is built using Flask, Gunicorn, and Postgres.

## Setup

The service can be launched through a preconfigured VSCode devcontainer or manually with `docker compose`.

### VSCode Devcontainer

1. Bottom left corner of VSCode, click the icon to open the dropdown menu
2. Select "Reopen in Container"

### Docker Compose

e.g.

```bash
cd .devcontainer
docker compose up --build -d
docker compose exec app /bin/bash
```

### Running the Service

Within the container, the service can be started with:

```bash
python3 -m gunicorn --log-level=info wsgi:app
```

When using `docker compose` directly, the service port is not exported by default. Either update the compose file or access the service through the container IP address[^1], or instead use the following command to create the containers and run the service with the port mapping:

```bash
docker compose run --rm -p 8080:8080 app python3 -m gunicorn --log-level=info wsgi:app
```

## Available API Endpoints

Routes return JSON responses and accept JSON request bodies where applicable. Routes return HTTP 200 OK unless otherwise specified, or when an erroneous request is made (returns HTTP 4xx).

### GET /products

List all products in the database. Takes optional query parameters to filter the results:

- `name`: Filter by product name
- `sku`: Filter by product SKU
- `min_price`: Filter by minimum price
- `max_price`: Filter by maximum price

Always returns a collection.

### GET /products/{product_id}

Retrieve a specific product by ID. Returns HTTP 404 Not Found if the product is not found.

### POST /products

Create a new product from JSON request body and returns the created product with HTTP 201 Created.

### PUT /products/{product_id}

Update an existing product from JSON request body. Request body must contain all fields. Returns the updated product or HTTP 404 Not Found if the product is not found.

### DELETE /products/{product_id}

Delete a product by ID. Always returns HTTP 204 No Content.

## Testing

Tests can be run using `pytest` through the `Makefile` from within the container:

```bash
make install
make test
```

[^1]: `docker inspect nyu-project | grep IPAddress`
