import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_read_item_valid_region():
    with patch('app.main.is_valid_region', return_value=True):
        with patch(
            'app.main.find_by_region',
            return_value=[{"name": "Pharmacy1"}]
        ):
            response = client.get("/query/1")
            assert response.status_code == 200
            assert "region" in response.json()
            assert "parapharmacies" in response.json()
            assert response.json()["parapharmacies"] == [{"name": "Pharmacy1"}]


def test_read_item_invalid_region_format():
    response = client.get("/query/invalid")
    assert response.status_code == 200
    assert response.json() == {
        "error": "Invalid format. Expecting a numeric region code"
    }


def test_read_item_invalid_region_code():
    with patch('app.main.is_valid_region', return_value=False):
        response = client.get("/query/999")
        assert response.status_code == 200
        assert "error" in response.json()


def test_get_date():
    response = client.get("/get-date")
    assert response.status_code == 200
    assert "date" in response.json()


def test_get_regions():
    response = client.get("/regions")
    assert response.status_code == 200
    assert "regions" in response.json()


def test_get_provinces():
    response = client.get("/regions/1/provinces")
    assert response.status_code == 200
    assert "provinces" in response.json()


def test_get_cities():
    response = client.get("/regions/1/provinces/province_name/cities")
    assert response.status_code == 200
    assert "cities" in response.json()


def test_get_pharmacies():
    response = client.get(
        "/regions/1/provinces/province_name/cities/city_name/pharmacies"
    )
    assert response.status_code == 200
    assert "pharmacies" in response.json()


@patch(
    'app.main.get_product_details',
    return_value={
        "VALID_PRODUCT": {
            "price": 10.0,
            "description": "A valid product."
        }
    }
)
def test_search_product_found(mock_get_product_details):
    response = client.get("/search-product?product_name=VALID_PRODUCT")
    assert response.status_code == 200
    assert "product" in response.json()
    assert response.json()["product"] == "VALID_PRODUCT"


def test_search_product_not_found():
    response = client.get(
        "/search-product?product_name=INVALID_PRODUCT"
    )
    assert response.status_code == 404
    assert response.json() == {
        "detail": (
            "The product 'INVALID_PRODUCT' is not available "
            "in the pharmacy."
        )
    }
