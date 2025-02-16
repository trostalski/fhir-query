# fhir-query-client

A Python client library for querying FHIR servers with support for both synchronous and asynchronous operations.

## Features

- Synchronous and asynchronous FHIR server querying
- Multiple authentication methods (Basic Auth, Token Auth, Login Auth)
- Support for GET and POST search requests
- Pagination handling
- Bundle response handling with DataFrame conversion
- Type hints and resource type validation

## Installation

```bash
pip install fhir-query-client
```

## Quick Start

### Synchronous Client

```python
from fhir_query_client import FhirQueryClient

# Initialize the client
client = FhirQueryClient(
    base_url="https://your-fhir-server.com/fhir",
    auth_method="basic",
    username="user",
    password="pass"
)

# Query patients
response = client.get(
    resource_type="Patient",
    params={"family": "Smith"}
)

# Access the results
patients = response.resources
first_patient = response.resource  # If only one result
```

### Asynchronous Client

```python
from fhir_query_client import AsyncFhirQueryClient
import asyncio

async def main():
    # Initialize the async client
    client = AsyncFhirQueryClient(
        base_url="https://your-fhir-server.com/fhir",
        auth_method="token",
        token="your-token"
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

The `FQCBundle` class provides convenient methods to work with FHIR Bundle responses:

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

## Advanced Usage

### Pagination

```python
# Get multiple pages of results
response = client.get(
    resource_type="Observation",
    params={"patient": "123"},
    pages=3  # Get up to 3 pages of results
)
```

### POST Search

```python
# Use POST for search instead of GET
response = client.get(
    resource_type="Patient",
    params={"_profile": "http://example.org/profile"},
    use_post=True
)
```

## License

[Add your license information here]

## Contributing

[Add contribution guidelines here]
