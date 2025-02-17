from unittest.mock import Mock, patch

import pytest
from aiohttp import ClientSession

from fhir_query.aclient import AsyncFhirQueryClient
from fhir_query.bundle import FhirQueryBundle


@pytest.fixture
def mock_session():
    session = Mock(spec=ClientSession)
    session.headers = {}
    return session


@pytest.fixture
def aclient(mock_session):
    return AsyncFhirQueryClient(
        base_url="https://test.fhir.server/fhir", session=mock_session
    )


def test_init():
    """Test client initialization"""
    client = AsyncFhirQueryClient(base_url="https://test.fhir.server/fhir")
    assert client.base_url == "https://test.fhir.server/fhir/"
    assert client.session is None


@pytest.mark.asyncio
async def test_get_with_params(aclient):
    """Test get method with query parameters"""
    response_data = {
        "resourceType": "Bundle",
        "type": "searchset",
        "entry": [{"resource": {"resourceType": "Patient", "id": "123"}}],
    }

    with patch.object(aclient, "make_request") as mock_make_request:
        mock_make_request.return_value = response_data

        result = await aclient.get(
            resource_type="Patient", params={"name": "Smith", "_count": "1"}
        )

        assert isinstance(result, FhirQueryBundle)
        mock_make_request.assert_called_once_with(
            method="GET",
            url="https://test.fhir.server/fhir/Patient?name=Smith&_count=1",
            headers={},
        )


@pytest.mark.asyncio
async def test_get_with_search_string(aclient):
    """Test get method with raw search string"""
    response_data = {
        "resourceType": "Bundle",
        "type": "searchset",
        "entry": [{"resource": {"resourceType": "Patient", "id": "123"}}],
    }

    with patch.object(aclient, "make_request") as mock_make_request:
        mock_make_request.return_value = response_data

        result = await aclient.get(
            resource_type="Patient", search_string="name=Smith&_count=1"
        )

        assert isinstance(result, FhirQueryBundle)
        mock_make_request.assert_called_once_with(
            method="GET",
            url="https://test.fhir.server/fhir/Patient?name=Smith&_count=1",
            headers={},
        )


@pytest.mark.asyncio
async def test_get_with_post_search(aclient):
    """Test get method using POST search"""
    response_data = {
        "resourceType": "Bundle",
        "type": "searchset",
        "entry": [{"resource": {"resourceType": "Patient", "id": "123"}}],
    }

    with patch.object(aclient, "make_request") as mock_make_request:
        mock_make_request.return_value = response_data

        result = await aclient.get(
            resource_type="Patient", params={"name": "Smith"}, use_post=True
        )

        assert isinstance(result, FhirQueryBundle)
        mock_make_request.assert_called_once_with(
            method="POST",
            url="https://test.fhir.server/fhir/Patient/_search",
            data='"name=Smith"',
            headers={},
        )


@pytest.mark.asyncio
async def test_get_with_pagination(aclient):
    """Test get method with pagination"""
    first_response = {
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

    second_response = {
        "resourceType": "Bundle",
        "type": "searchset",
        "entry": [{"resource": {"resourceType": "Patient", "id": "456"}}],
    }

    with patch.object(aclient, "make_request") as mock_make_request:
        mock_make_request.side_effect = [first_response, second_response]

        result = await aclient.get(
            resource_type="Patient", params={"name": "Smith"}, pages=2
        )

        assert isinstance(result, FhirQueryBundle)
        assert len(mock_make_request.call_args_list) == 2


def test_basic_auth_setup(aclient):
    """Test basic authentication setup"""
    aclient._setup_basic_auth("username", "password")
    assert "Authorization" in aclient._headers
    assert aclient._headers["Authorization"].startswith("Basic ")


def test_token_auth_setup(aclient):
    """Test token authentication setup"""
    token = "my-test-token"
    aclient._setup_token_auth(token)
    assert aclient._headers["Authorization"] == f"Bearer {token}"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "input_params",
    [
        ({"params": {"name": "Smith"}, "search_string": "name=Smith"}),
        ({"params": {"name": "Smith"}, "full_url": True}),
        ({"search_string": "name=Smith", "full_url": True}),
    ],
)
async def test_get_invalid_param_combination(aclient, input_params):
    """Test that providing multiple search options raises an assertion error"""
    with pytest.raises(AssertionError):
        await aclient.get(resource_type="Patient", **input_params)


@pytest.mark.asyncio
async def test_login_auth_missing_credentials(aclient):
    """Test login authentication with missing credentials"""
    aclient.login_url = "https://test.fhir.server/login"

    with pytest.raises(ValueError, match="Username and password are required"):
        await aclient._setup_login_auth()


@pytest.mark.asyncio
async def test_login_auth_missing_url(aclient):
    """Test login authentication with missing login URL"""
    aclient.username = "test_user"
    aclient.password = "test_pass"

    with pytest.raises(ValueError, match="login_url is required"):
        await aclient._setup_login_auth()
