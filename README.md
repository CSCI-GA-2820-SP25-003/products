# NYU Devops Products Service

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
[![CI Build](https://github.com/CSCI-GA-2820-SP25-003/products/actions/workflows/tdd-test.yml/badge.svg)](https://github.com/CSCI-GA-2820-SP25-003/products/actions/workflows/tdd-test.yml)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-SP25-003/products/graph/badge.svg?token=RQ9NKJ0LIX)](https://codecov.io/gh/CSCI-GA-2820-SP25-003/products)


## Overview

This service provides a RESTful API for the Products database to store and manage product information. The service source code is contained in the `/service` directory and related test functions are in the `/tests` directory. The service is built using Flask, Gunicorn, and Postgres.

The service is currently deployed at the following URL: https://products-mz3921-dev.apps.rm1.0a51.p1.openshiftapps.com/

## Setup

The service can be launched through one of the following options:

- VSCode Devcontainer
- Docker Compose
- Kubernetes (locally via k3d)

### 1. VSCode Devcontainer

1. Bottom left corner of VSCode, click the icon to open the dropdown menu
2. Select "Reopen in Container"

### 2. Docker Compose

e.g.

```bash
cd .devcontainer
docker compose up --build -d
docker compose exec app /bin/bash
```

### 3. Kubernetes (k3d)

Create a k8s cluster
```bash
make cluster
```

Build and push docker images
```bash
docker build -t products:1.0 .
docker tag products:1.0 cluster-registry:5000/products:1.0
docker push cluster-registry:5000/products:1.0
```

Deploy k8s resources
```bash
kubectl apply -f k8s/postgres/
kubectl apply -f k8s/
```


## Running the Service 

#### 1. VScode Devcontainer / Docker Compose
Within the container, the service can be started with:

```bash
make install
make run
```

If run through the devcontainer, the service will be available at `http://localhost:8080`.

When using `docker compose` directly, the service port is not exported by default. Either update the compose file or access the service through the container IP address[^1], or instead use the following command to create the containers and run the service with the port mapping:

```bash
docker compose run --rm -p 8080:8080 app bash -c "make install && make run"
```

#### 2. Kubernetes (k3d)
Check if all PODs are running
```bash
kubectl get pods
kubectl get services
kubectl get ingress
```

Then access the application at `http://localhost:8080/`

e.g.

```bash
curl http://localhost:8080/
```

## Structure

### Database

The internal database has the following structure:

- `id` (int): Internal identifier, primary key
- `sku` (str < 63): Product SKU, unique, not null
- `name` (str < 63): Product name, not null
- `description` (str < 256): Product description
- `price` (fixed point decimal): Product price, not null
- `image_url` (str < 256): URL to product image
- `created_time` (datetime): Timestamp of creation, not null
- `updated_time` (datetime): Timestamp of last update, not null
- `likes` (int): Number of likes the product receives

The `image_url` field is not validated but should be a valid URL to an image.

The `price` field is stored as a fixed point decimal with 10 digits and 2 decimal places. Fields below containing this decimal format (or string formatted decimal) will be denoted as "price-like"

The fields `id`, `created_time`, and `updated_time` are automatically generated internally and should not be provided by requests.

### Product Response JSON

The format of the product JSON returned by some routes is as follows:

- `id` (int): Internal identifier
- `sku` (str): Product SKU
- `name` (str): Product name
- `description` (str): Product description
- `price` (str price-like): Product price
- `image_url` (str): URL to product image
- `created_time` (str): UTC Timestamp of creation in ISO 8601 format
- `updated_time` (str): UTC Timestamp of last update in ISO 8601 format
- `likes` (int): Number of likes the product receives


### Product Request JSON

The format of the product JSON expected by some routes is similar to the response format, but with some differences.

Requests which require a product JSON body should not contain the `id`, `created_time`, or `updated_time` fields

The `description` and `image_url` fields are optional and can be omitted.

All other fields (`sku`, `name`, `price`) are required.

## Available API Endpoints

The API base URL is `/api`. The routes below can be accessed using the base URL in addition to the paths below.

Routes return JSON responses and accept JSON request bodies where applicable. Routes return HTTP 200 OK unless otherwise specified, or when an erroneous request is made (returns HTTP 4xx).

The `product_id` query parameter referenced in multiple routes is an internal identifier first assigned when creating a product. The value is available in the `id` field.

### GET /

Returns information about the service

Example response:

```json
{
    "name": "Product Demo REST API Service",
    "paths": "http://127.0.0.1:8080/products",
    "version": "1.0"
}
```

### GET /products

List all products in the database. Takes optional query parameters to filter the results:

- `name` (str): Filter by product name
- `sku` (str): Filter by product SKU
- `min_price` (price-like): Filter by minimum price
- `max_price` (price-like): Filter by maximum price

Always returns a collection.

Example response:

```json
[
    {
        "created_time": "2025-03-05T00:43:12.963282",
        "description": "unknown",
        "id": 1009,
        "image_url": "https://www.google.com",
        "name": "Vacuum Cleaner",
        "price": "233.73",
        "sku": "123123123",
        "updated_time": "2025-03-05T00:43:12.964258"
    },
    {
        "created_time": "2025-03-05T00:43:12.972948",
        "description": "Sample description",
        "id": 1010,
        "image_url": "https://www.google.com",
        "name": "Vacuum Cleaner",
        "price": "496.16",
        "sku": "123123123",
        "updated_time": "2025-03-05T00:43:12.972948"
    }
]
```

### GET /products/{product_id}

Retrieve a specific product by ID. Returns HTTP 404 Not Found if the product is not found.

Example response to `/products/1009`:

```json
{
    "created_time": "2025-03-05T00:43:12.963282",
    "description": "unknown",
    "id": 1009,
    "image_url": "https://www.google.com",
    "name": "Vacuum Cleaner",
    "price": "233.73",
    "sku": "123123123",
    "updated_time": "2025-03-05T00:43:12.964258"
}
```

### POST /products

Create a new product from JSON request body and returns the created product with HTTP 201 Created.

Example request: `POST /products`:

```json
{
    "description": "unknown",
    "image_url": "https://example.com",
    "name": "test product",
    "price": "350.00",
    "sku": "123123123"
}
```

Example response:

```json
{
    "created_time": "2025-03-05T07:13:08.443724",
    "description": "unknown",
    "id": 1012,
    "image_url": "http://example.com",
    "name": "test product",
    "price": "350.00",
    "sku": "123123123",
    "updated_time": "2025-03-05T07:13:08.443724"
}
```

### PUT /products/{product_id}

Update an existing product from JSON request body. Request body must contain all fields. Returns the updated product or HTTP 404 Not Found if the product is not found.

Example request: `PUT /products/1012`:

```json
{
    "description": "New description",
    "image_url": "https://example.com",
    "name": "test product updated",
    "price": "400.00",
    "sku": "123123123"
}
```

Example response:

```json
{
    "created_time": "2025-03-05T07:13:08.443724",
    "description": "New description",
    "id": 1012,
    "image_url": "https://example.com",
    "name": "test product updated",
    "price": "400.00",
    "sku": "123123123",
    "updated_time": "2025-03-05T07:16:56.602542"
}
```

### DELETE /products/{product_id}

Delete a product by ID. Always returns HTTP 204 No Content.


### PUT /products/{product_id}/like

Like an existing product by ID. Increments the product's likes count. Returns the updated product or HTTP 404 Not Found if the product is not found.

Example request: `PUT /products/1012/like`:

```json
{}
```

Example response:

```json
{
    "created_time": "2025-03-05T07:13:08.443724",
    "description": "New description",
    "id": 1012,
    "image_url": "https://example.com",
    "name": "test product updated",
    "price": "400.00",
    "sku": "123123123",
    "updated_time": "2025-03-05T07:20:42.123456",
    "likes": 1
}
```

## Testing  

Tests can be run using `pytest` through the `Makefile` from within the container:

```bash
make install
make test
```

[^1]: `docker inspect nyu-project | grep IPAddress`

## License
Copyright (c) 2016, 2025 John Rofrano. All rights reserved.

Licensed under the Apache License. See LICENSE

This repository is part of the New York University (NYU) masters class: CSCI-GA.2820-001 DevOps and Agile Methodologies created and taught by John Rofrano, Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
