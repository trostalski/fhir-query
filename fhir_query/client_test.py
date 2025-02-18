from unittest.mock import Mock

import pytest
from requests import Response, Session

from fhir_query.bundle import FhirQueryBundle
from fhir_query.client import FhirQueryClient


@pytest.fixture
def mock_session():
    session = Mock(spec=Session)
    session.headers = {}
    return session


@pytest.fixture
def client(mock_session):
    return FhirQueryClient(
        base_url="https://test.fhir.server/fhir", session=mock_session
    )


@pytest.fixture
def mock_response():
    response = Mock(spec=Response)
    response.status_code = 200
    response.json.return_value = {
        "resourceType": "Bundle",
        "type": "searchset",
        "entry": [{"resource": {"resourceType": "Patient", "id": "123"}}],
    }
    return response


def test_init():
    """Test client initialization"""
    client = FhirQueryClient(base_url="https://test.fhir.server/fhir")
    assert client.base_url == "https://test.fhir.server/fhir/"
    assert isinstance(client.session, Session)


def test_get_with_params(client, mock_response):
    """Test get method with query parameters"""
    client.session.request.return_value = mock_response

    result = client.get(
        resource_type="Patient", params={"name": "Smith", "_count": "1"}
    )

    assert isinstance(result, FhirQueryBundle)
    client.session.request.assert_called_once_with(
        "GET",
        "https://test.fhir.server/fhir/Patient?name=Smith&_count=1",
        json=None,
        headers=None,
    )


def test_get_with_search_string(client, mock_response):
    """Test get method with raw search string"""
    client.session.request.return_value = mock_response

    result = client.get(resource_type="Patient", search_string="name=Smith&_count=1")

    assert isinstance(result, FhirQueryBundle)
    client.session.request.assert_called_once_with(
        "GET",
        "https://test.fhir.server/fhir/Patient?name=Smith&_count=1",
        json=None,
        headers=None,
    )


def test_get_with_post_search(client, mock_response):
    """Test get method using POST search"""
    mock_response.json.return_value = {
        "resourceType": "Bundle",
        "type": "searchset",
        "entry": [{"resource": {"resourceType": "Patient", "id": "123"}}],
    }
    client.session.request.return_value = mock_response

    result = client.get(
        resource_type="Patient", params={"name": "Smith"}, use_post=True
    )

    assert isinstance(result, FhirQueryBundle)
    client.session.request.assert_called_once_with(
        "POST",
        "https://test.fhir.server/fhir/Patient/_search",
        json='"name=Smith"',
        headers=None,
    )


def test_get_with_pagination(client):
    """Test get method with pagination"""
    # Create responses for initial request and subsequent page
    first_response = Mock(spec=Response)
    first_response.status_code = 200
    first_response.json.return_value = {
        "resourceType": "Bundle",
        "type": "searchset",
        "link": [
            {
                "relation": "next",
                "url": "https://test.fhir.server/fhir/Patient?page=2",
            }
        ],
        "entry": [{"resource": {"resourceType": "Patient", "id": "123"}}],
    }

    second_response = Mock(spec=Response)
    second_response.status_code = 200
    second_response.json.return_value = {
        "resourceType": "Bundle",
        "type": "searchset",
        "entry": [{"resource": {"resourceType": "Patient", "id": "456"}}],
    }

    client.session.request.side_effect = [first_response, second_response]

    result = client.get(resource_type="Patient", params={"name": "Smith"}, pages=2)

    assert isinstance(result, FhirQueryBundle)
    assert len(client.session.request.call_args_list) == 2


def test_basic_auth_setup(client):
    """Test basic authentication setup"""
    client._setup_basic_auth("username", "password")
    assert "Authorization" in client.session.headers
    assert client.session.headers["Authorization"].startswith("Basic ")


def test_token_auth_setup(client):
    """Test token authentication setup"""
    token = "my-test-token"
    client._setup_token_auth(token)
    assert client.session.headers["Authorization"] == f"Bearer {token}"


@pytest.mark.parametrize(
    "input_params",
    [
        ({"params": {"name": "Smith"}, "search_string": "name=Smith"}),
        ({"params": {"name": "Smith"}, "full_url": True}),
        ({"search_string": "name=Smith", "full_url": True}),
    ],
)
def test_get_invalid_param_combination(client, input_params):
    """Test that providing multiple search options raises an assertion error"""
    with pytest.raises(AssertionError):
        client.get(resource_type="Patient", **input_params)


def test_login_auth_setup(client, mock_response):
    """Test login-based authentication"""
    mock_response.text = "test-token"
    client.session.get.return_value = mock_response

    client.username = "test_user"
    client.password = "test_pass"
    client._setup_login_auth(login_url="https://test.fhir.server/login")

    client.session.get.assert_called_once_with(
        "https://test.fhir.server/login", auth=("test_user", "test_pass"), headers={}
    )
    assert client.session.headers["Authorization"] == "Bearer test-token"


def test_login_auth_missing_credentials(client):
    """Test login authentication with missing credentials"""
    with pytest.raises(ValueError, match="Username and password are required"):
        client._setup_login_auth(login_url="https://test.fhir.server/login")
