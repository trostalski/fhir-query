# fhir-query

A simple Python client library for querying FHIR servers. Sync and async support.

## Features

- Synchronous and asynchronous FHIR server querying
- Multiple authentication methods (Basic Auth, Token Auth, Login Auth)
- Support for GET and POST search requests
- Pagination handling
- Bundle response handling with DataFrame conversion
- Type hints and resource type validation

## Installation

```bash
pip install fhir-query
```

## Quick Start

### Synchronous Client

```python
from fhir_query import FhirQueryClient

# Initialize the client
client = FhirQueryClient(
    base_url="https://hapi.fhir.org/baseR4/",
)

# Query patients
response = client.get(
    resource_type="Patient",
    params={"family": "Smith"}
)

# Access the raw bundle
bundle = response.data

# Access the resources
resources = bundle.resources
```

### Asynchronous Client

```python
from fhir_query import AsyncFhirQueryClient
import asyncio

async def main():
    # Initialize the async client
    client = AsyncFhirQueryClient(
        base_url="https://hapi.fhir.org/baseR4/",
    )

    # Query patients
    response = await client.get(
        resource_type="Patient",
        params={"gender": "female"}
    )

    # Convert to DataFrame
    df = response.to_df()
    print(df)

asyncio.run(main())
```

## Authentication Methods

The client supports three authentication methods:

- `basic`: Basic HTTP authentication with username and password
- `token`: Bearer token authentication
- `login`: Login-based authentication that obtains a token from a login endpoint

## Bundle Handling

The `FhirQueryBundle` class provides convenient methods to work with FHIR Bundle responses:

```python
# Get total count
total_count = bundle.total

# Access resources
resources = bundle.resources

# Convert to DataFrame
df = bundle.to_df()

# Pagination
next_link = bundle.next_link
previous_link = bundle.previous_link
```
