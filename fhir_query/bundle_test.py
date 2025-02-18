from typing import Any, Dict

import pandas as pd
import pytest

from fhir_query.bundle import FhirQueryBundle


# Test fixtures
@pytest.fixture
def empty_bundle() -> Dict[str, Any]:
    return {"resourceType": "Bundle", "type": "searchset", "entry": []}


@pytest.fixture
def patient_bundle() -> Dict[str, Any]:
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": 2,
        "entry": [
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "patient-1",
                    "name": [{"given": ["John"], "family": "Doe"}],
                    "birthDate": "1970-01-01",
                }
            },
            {
                "resource": {
                    "resourceType": "Patient",
                    "id": "patient-2",
                    "name": [{"given": ["Jane"], "family": "Smith"}],
                    "birthDate": "1980-02-02",
                }
            },
        ],
    }


@pytest.fixture
def mixed_bundle() -> Dict[str, Any]:
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "entry": [
            {"resource": {"resourceType": "Patient", "id": "patient-1"}},
            {
                "resource": {
                    "resourceType": "Observation",
                    "id": "obs-1",
                    "subject": {"reference": "Patient/patient-1"},
                }
            },
        ],
    }


@pytest.fixture
def condition_bundle() -> Dict[str, Any]:
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "entry": [
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": "cond-1",
                    "category": [{"coding": [{"display": "Problem List"}]}],
                    "code": {
                        "coding": [
                            {"display": "Diabetes", "code": "E11", "system": "ICD-10"}
                        ]
                    },
                    "subject": {"reference": "Patient/123"},
                    "encounter": {"reference": "Encounter/456"},
                    "recordedDate": "2023-01-01",
                }
            }
        ],
    }


@pytest.fixture
def observation_bundle() -> Dict[str, Any]:
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "entry": [
            {
                "resource": {
                    "resourceType": "Observation",
                    "id": "obs-1",
                    "category": [{"coding": [{"display": "Vital Signs"}]}],
                    "code": {"coding": [{"display": "Blood Pressure"}]},
                    "valueQuantity": {"value": 120, "unit": "mmHg"},
                    "subject": {"reference": "Patient/123"},
                    "encounter": {"reference": "Encounter/456"},
                    "effectiveDateTime": "2023-01-01",
                }
            }
        ],
    }


def test_init_with_bundle(patient_bundle):
    bundle = FhirQueryBundle(patient_bundle)
    assert bundle.size == 2
    assert bool(bundle)


def test_init_with_single_resource():
    resource = {"resourceType": "Patient", "id": "test"}
    bundle = FhirQueryBundle(
        {"resourceType": "Bundle", "entry": [{"resource": resource}]}
    )
    assert bundle.size == 1
    assert bundle.resource == resource


def test_empty_bundle(empty_bundle):
    bundle = FhirQueryBundle(empty_bundle)
    assert not bool(bundle)
    assert bundle.size == 0


def test_collect_resource_types(mixed_bundle):
    bundle = FhirQueryBundle(mixed_bundle)
    types = bundle.collect_resource_types()
    assert set(types) == {"Patient", "Observation"}


def test_collect_resources_by_type(mixed_bundle):
    bundle = FhirQueryBundle(mixed_bundle)
    patients = bundle.collect_resources_by_type("Patient")
    assert len(patients) == 1
    assert patients[0]["id"] == "patient-1"


def test_collect_ids(patient_bundle):
    bundle = FhirQueryBundle(patient_bundle)
    ids = bundle.collect_ids()
    assert ids == ["patient-1", "patient-2"]


def test_to_df(patient_bundle):
    bundle = FhirQueryBundle(patient_bundle)
    columns = {"id": "id", "family_name": "name[0].family", "birth_date": "birthDate"}
    df = bundle.to_df(columns)
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == ["id", "family_name", "birth_date"]
    assert len(df) == 2


def test_to_df_empty_bundle_raises(empty_bundle):
    bundle = FhirQueryBundle(empty_bundle)
    with pytest.raises(ValueError, match="Bundle is empty and no columns specified"):
        bundle.to_df()


def test_iteration(patient_bundle):
    bundle = FhirQueryBundle(patient_bundle)
    resources = [resource for resource in bundle]
    assert len(resources) == 2
    assert all(r["resourceType"] == "Patient" for r in resources)


def test_getitem(patient_bundle):
    bundle = FhirQueryBundle(patient_bundle)
    assert bundle[0]["resourceType"] == "Patient"
    assert bundle[0]["id"] == "patient-1"


def test_len(patient_bundle):
    bundle = FhirQueryBundle(patient_bundle)
    assert len(bundle) == 2


def test_contains(patient_bundle):
    bundle = FhirQueryBundle(patient_bundle)
    resource = bundle[0]
    assert resource in bundle


def test_bundle_properties():
    bundle_data = {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": 100,
        "link": [
            {"relation": "next", "url": "http://example.com/next"},
            {"relation": "previous", "url": "http://example.com/prev"},
        ],
        "entry": [{"resource": {"resourceType": "Patient", "id": "1"}}],
    }
    bundle = FhirQueryBundle(bundle_data)

    assert bundle.total == 100
    assert bundle.next_link == "http://example.com/next"
    assert bundle.previous_link == "http://example.com/prev"


def test_str_and_repr(patient_bundle):
    bundle = FhirQueryBundle(patient_bundle)
    str_repr = str(bundle)
    repr_str = repr(bundle)
    assert "FQCBundle" in str_repr
    assert "size=2" in str_repr
    assert "FQCBundle" in repr_str
    assert "size=2" in repr_str


def test_add_bundle():
    initial_bundle = {
        "resourceType": "Bundle",
        "entry": [{"resource": {"resourceType": "Patient", "id": "1"}}],
    }
    additional_bundle = {
        "resourceType": "Bundle",
        "entry": [{"resource": {"resourceType": "Patient", "id": "2"}}],
    }

    bundle = FhirQueryBundle(initial_bundle)
    assert bundle.size == 1

    bundle.add_bundle(additional_bundle)
    assert bundle.size == 2
