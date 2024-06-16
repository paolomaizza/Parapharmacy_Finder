import pytest
from flask import Flask, render_template_string, request
from flask.testing import FlaskClient
from unittest.mock import patch
from bs4 import BeautifulSoup
from app.main import app, fetch_regions_from_backend

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    soup = BeautifulSoup(response.data, 'html.parser')
    assert soup.title.string == "Parapharmacy Finder"

def test_internal_get(client):
    with patch('app.main.fetch_regions_from_backend', return_value=[
        {"code": 1, "name": "Region1"},
        {"code": 2, "name": "Region2"}
    ]):
        response = client.get('/internal')
        assert response.status_code == 200
        soup = BeautifulSoup(response.data, 'html.parser')
        assert "Search Product" in soup.text
        assert "Search Location" in soup.text
        assert "Get Directions" in soup.text

def test_internal_post_success(client):
    with patch('app.main.fetch_regions_from_backend', return_value=[
        {"code": 1, "name": "Region1"},
        {"code": 2, "name": "Region2"}
    ]):
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {'parapharmacies': [
                {"name": "Parapharmacy1", "address": "Address1", "cap": "1001", "city": "City1"},
                {"name": "Parapharmacy2", "address": "Address2", "cap": "1002", "city": "City2"}
            ]}
            response = client.post('/internal', data={'region': '1'})
            assert response.status_code == 200
            soup = BeautifulSoup(response.data, 'html.parser')
            assert "Parapharmacy1" in soup.text
            assert "Parapharmacy2" in soup.text

def test_internal_post_invalid_region(client):
    with patch('app.main.fetch_regions_from_backend', return_value=[
        {"code": 1, "name": "Region1"},
        {"code": 2, "name": "Region2"}
    ]):
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 404
            mock_get.return_value.json.return_value = {'detail': 'Region not found'}
            response = client.post('/internal', data={'region': '999'})
            assert response.status_code == 200
            soup = BeautifulSoup(response.data, 'html.parser')
            assert "Invalid region code 999" in soup.text, f"Response data: {soup.prettify()}"

def test_internal_post_no_parapharmacies(client):
    with patch('app.main.fetch_regions_from_backend', return_value=[
        {"code": 1, "name": "Region1"},
        {"code": 2, "name": "Region2"}
    ]):
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {'parapharmacies': []}
            response = client.post('/internal', data={'region': '1'})
            assert response.status_code == 200
            soup = BeautifulSoup(response.data, 'html.parser')
            assert "No parapharmacies available in region 1" in soup.text, f"Response data: {soup.prettify()}"

def test_fetch_regions_from_backend_success():
    mock_response = {
        "regions": [
            {"code": "1", "name": "Region1"},
            {"code": "2", "name": "Region2"}
        ]
    }
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response
        
        regions = fetch_regions_from_backend()
        assert regions == mock_response["regions"]

def test_fetch_regions_from_backend_failure():
    with patch('requests.get') as mock_get:
        mock_get.return_value.status_code = 500
        mock_get.return_value.json.return_value = None  # Ensure the response json is None

        regions = fetch_regions_from_backend()
        assert regions == "Regions not available"

