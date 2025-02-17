from typing import Any, Generator, Literal

import pandas as pd
from fhirpathpy import compile


def get_link(bundle: dict, relation: Literal["next", "previous", "self"]) -> str | None:
    """Extract a link from a FHIR Bundle.

    Args:
        bundle: FHIR Bundle resource containing link relations.
        relation: The relation to extract.
    """
    if "link" not in bundle:
        return None
    for link in bundle["link"]:
        if link["relation"] == relation:
            return link["url"]
    return None


def get_next_link(bundle: dict) -> str | None:
    """Extract the 'next' link from a FHIR Bundle.

    Args:
        bundle: FHIR Bundle resource containing link relations.

    Returns:
        str | None: Absolute URL for the 'next' relation if present, None otherwise.
    """
    return get_link(bundle, "next")


def get_previous_link(bundle: dict) -> str | None:
    """Extract the 'previous' link from a FHIR Bundle.

    Args:
        bundle: FHIR Bundle resource containing link relations.

    Returns:
        str | None: Absolute URL for the 'previous' relation if present, None otherwise.
    """
    return get_link(bundle, "previous")


def get_self_link(bundle: dict) -> str | None:
    """Extract the 'self' link from a FHIR Bundle.

    Args:
        bundle: FHIR Bundle resource containing link relations.

    Returns:
        str | None: Absolute URL for the 'self' relation if present, None otherwise.
    """
    return get_link(bundle, "self")


def get_resources_from_bundle(bundle: dict) -> list[dict]:
    """Extract resources from a FHIR Bundle.

    Args:
        bundle: FHIR Bundle resource containing resources.
    """
    return [entry["resource"] for entry in bundle.get("entry", [])]


def bundle_to_df(bundle: dict, columns: dict[str, str]) -> pd.DataFrame:
    """
    Convert a bundle or single resource dictionary to a pandas DataFrame.
    Args:
        bundle (dict): The FHIR bundle to convert to a DataFrame.
        columns (dict[str, str]): A mapping of desired column names to FHIR paths.
    Returns:
        pd.DataFrame: The converted DataFrame.
    Raises:
        ImportError: If pandas is not installed.
        ValueError: If input data is not a bundle.
    """
    # Directly create rows with all columns
    rows = collect_many_paths(bundle, columns)
    return pd.DataFrame(rows)


def collect_many_paths(bundle: dict, paths: dict[str, str]) -> list[dict[str, Any]]:
    """
    Collect multiple elements from a bundle using a dot-separated path for each element.
    Args:
        bundle (dict): The FHIR bundle to process
        paths (Dict[str, str]): Dictionary mapping keys to dot-separated paths
    Returns:
        list[dict[str, Any]]: List of dictionaries containing the collected values
    """
    # Compile all paths once
    path_fns = {key: compile(path) for key, path in paths.items()}

    results = []
    for resource in resource_iter(bundle):
        row = {}
        for key, path_fn in path_fns.items():
            values = path_fn(resource)
            row[key] = (
                values[0] if values and len(values) == 1 else values if values else None
            )
        results.append(row)

    return results


def resource_iter(bundle: dict) -> Generator[dict[str, Any], None, None]:
    """Create an iterator over all resources in a FHIR Bundle.

    Args:
        bundle: FHIR Bundle resource.

    Returns:
        Generator[dict[str, Any], None, None]: Generator yielding each resource in the bundle.
    """
    return (entry["resource"] for entry in bundle["entry"])


def get_id_from_reference(reference: dict) -> str:
    """Extract the resource ID from a FHIR reference.

    Args:
        reference: FHIR reference string (e.g., {"reference": "Patient/123"}).

    Returns:
        str: The extracted resource ID.
    """
    return reference.get("reference", "").split("/")[-1]


def get_id_from_reference_url(reference: dict) -> str:
    """Extract the resource ID from a FHIR reference URL.

    Args:
        reference: FHIR reference string (e.g., {"reference": "Patient/123"}).

    Returns:
        str: The extracted resource ID.
    """
    return reference.get("reference", "").split("/")[-1]
