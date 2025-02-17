# FHIR Query Client

A Python library for querying FHIR servers with both synchronous and asynchronous support.

## Installation

pip install fhir-query

## Quick Start

### Synchronous Client

from fhir_query import FhirQueryClient

# Initialize the client

client = FhirQueryClient(
base_url="https://hapi.fhir.org/baseR4/",
)

# Simple GET request

patients = client.get("Patient")

# Query with parameters

search_params = {
"gender": "female",
"birthdate": "gt2000-01-01"
}
female_patients = client.get("Patient", params=search_params)

# Convert results to DataFrame

df = female_patients.to_df()

### Asynchronous Client

from fhir_query import AsyncFhirQueryClient
import asyncio

async def main(): # Initialize the async client
client = AsyncFhirQueryClient(
base_url="https://hapi.fhir.org/baseR4/"
)

    # Fetch resources asynchronously
    patients = await client.get("Patient")

    # Process results
    print(f"Found {patients.total} patients")

asyncio.run(main())

## Authentication

The library supports multiple authentication methods:

### Basic Authentication

client = FhirQueryClient(
base_url="https://hapi.fhir.org/baseR4/",
auth_method="basic",
username="user",
password="pass"
)

### Token Authentication

client = FhirQueryClient(
base_url="https://hapi.fhir.org/baseR4/",
auth_method="token",
token="your-bearer-token"
)

### Login Authentication

client = FhirQueryClient(
base_url="https://hapi.fhir.org/baseR4/",
auth_method="login",
login_url="https://hapi.fhir.org/baseR4/login",
username="user",
password="pass"
)

## Working with Bundles

The `FhirQueryBundle` class provides convenient methods to work with FHIR Bundle responses:

# Get a bundle of resources

bundle = client.get("Patient")

# Access properties

print(f"Total resources: {bundle.total}")
print(f"Bundle size: {bundle.size}")

# Access individual resources

first_patient = bundle.resource # When expecting single resource
all_patients = bundle.resources # List of all resources

# Convert to DataFrame

df = bundle.to_df()

# Pagination

next_url = bundle.next_link
prev_url = bundle.previous_link

# Resource filtering

resource_types = bundle.collect_resource_types()
patient_resources = bundle.collect_resources_by_type("Patient")
resource_ids = bundle.collect_ids()

## Advanced Features

### Pagination Support

# Fetch multiple pages

results = client.get("Patient", pages=3) # Fetches up to 3 pages

# Manual pagination using next_link

while bundle.next_link:
next_bundle = client.get("Patient", full_url=bundle.next_link)
bundle.add_bundle(next_bundle.data)

### POST Search

# Use POST for search requests (useful for long queries)

client = FhirQueryClient(
base_url="https://hapi.fhir.org/baseR4/",
use_post=True
)

# Or specify per-request

results = client.get("Patient", use_post=True, params=search_params)

### Custom Headers

# Add custom headers for specific requests

headers = {
"Prefer": "handling=strict",
"Accept-Language": "en-US"
}
results = client.get("Patient", headers=headers)

## Error Handling

The client will raise appropriate exceptions for HTTP errors and invalid responses:

- HTTP errors will raise `requests.exceptions.HTTPError`
- Invalid authentication configuration will raise `ValueError`
- Multiple resources when expecting single will raise `ValueError`

## Logging

The library uses Python's standard logging module. Enable debug logging to see detailed request information:

import logging
logging.basicConfig(level=logging.DEBUG)

## Contributing

Contributions are welcome! Please visit our GitHub repository to submit issues or pull requests.

## License

[Add your license information here]
