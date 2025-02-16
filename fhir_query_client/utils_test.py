import pandas as pd
import pytest

from fhir_query_client.utils import (bundle_to_df, collect_many_paths,
                                     get_id_from_reference,
                                     get_id_from_reference_url, get_link,
                                     get_next_link, get_previous_link,
                                     get_resources_from_bundle, get_self_link,
                                     resource_iter)


@pytest.fixture
def sample_bundle():
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "link": [
            {"relation": "self", "url": "https://api/Patient"},
            {"relation": "next", "url": "https://api/Patient?page=2"},
            {"relation": "previous", "url": "https://api/Patient?page=1"},
        ],
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "123",
                    "name": [{"given": ["John"], "family": "Doe"}],
                }
            },
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "456",
                    "name": [{"given": ["Jane"], "family": "Smith"}],
                }
            },
        ],
    }


def test_get_link(sample_bundle):
    assert get_link(sample_bundle, "next") == "https://api/Patient?page=2"
    assert get_link(sample_bundle, "self") == "https://api/Patient"
    assert get_link(sample_bundle, "previous") == "https://api/Patient?page=1"
    assert get_link({}, "next") is None
    assert get_link({"link": []}, "next") is None


def test_get_next_link(sample_bundle):
    assert get_next_link(sample_bundle) == "https://api/Patient?page=2"
    assert get_next_link({}) is None


def test_get_previous_link(sample_bundle):
    assert get_previous_link(sample_bundle) == "https://api/Patient?page=1"
    assert get_previous_link({}) is None


def test_get_self_link(sample_bundle):
    assert get_self_link(sample_bundle) == "https://api/Patient"
    assert get_self_link({}) is None


def test_get_resources_from_bundle(sample_bundle):
    resources = get_resources_from_bundle(sample_bundle)
    assert len(resources) == 2
    assert resources[0]["id"] == "123"
    assert resources[1]["id"] == "456"
    assert get_resources_from_bundle({}) == []


def test_bundle_to_df(sample_bundle):
    columns = {
        "id": "id",
        "given_name": "name[0].given[0]",
        "family_name": "name[0].family",
    }
    df = bundle_to_df(sample_bundle, columns)

    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert list(df.columns) == ["id", "given_name", "family_name"]
    assert df.iloc[0]["id"] == "123"
    assert df.iloc[0]["given_name"] == "John"
    assert df.iloc[0]["family_name"] == "Doe"


def test_collect_many_paths(sample_bundle):
    paths = {
        "id": "id",
        "given_name": "name[0].given[0]",
        "family_name": "name[0].family",
    }
    results = collect_many_paths(sample_bundle, paths)

    assert len(results) == 2
    assert results[0]["id"] == "123"
    assert results[0]["given_name"] == "John"
    assert results[0]["family_name"] == "Doe"


def test_resource_iter(sample_bundle):
    resources = list(resource_iter(sample_bundle))
    assert len(resources) == 2
    assert resources[0]["id"] == "123"
    assert resources[1]["id"] == "456"


def test_get_id_from_reference():
    reference = {"reference": "Patient/123"}
    assert get_id_from_reference(reference) == "123"
    assert get_id_from_reference({}) == ""
    assert get_id_from_reference({"reference": ""}) == ""


def test_get_id_from_reference_url():
    reference = {"reference": "https://api/Patient/123"}
    assert get_id_from_reference_url(reference) == "123"
    assert get_id_from_reference_url({}) == ""
    assert get_id_from_reference_url({"reference": ""}) == ""
