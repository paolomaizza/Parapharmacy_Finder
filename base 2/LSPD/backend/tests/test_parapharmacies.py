import pytest
import pandas as pd
from unittest.mock import patch
from app.mymodules.parapharmacies import (
    find_by_region,
    is_valid_region,
    list_regions,
    list_provinces,
    list_cities,
    find_by_region_province_and_city
)

# Sample data for mocking
mock_data = pd.DataFrame({
    'CODICEREGIONE': [1, 1, 2],
    'DESCRIZIONEREGIONE': ['Region1', 'Region1', 'Region2'],
    'DESCRIZIONEPROVINCIA': ['Province1', 'Province2', 'Province3'],
    'DESCRIZIONECOMUNE': ['City1', 'City2', 'City3'],
    'DENOMINAZIONESITO': ['Pharmacy1', 'Pharmacy2', 'Pharmacy3'],
    'INDIRIZZO': ['Address1', 'Address2', 'Address3'],
    'CAP': ['00100', '00200', '00300']
})


@patch('app.mymodules.parapharmacies.df', mock_data)
def test_find_by_region():
    result = find_by_region(1)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]['name'] == 'Pharmacy1'


@patch('app.mymodules.parapharmacies.df', mock_data)
def test_is_valid_region():
    assert is_valid_region(1)
    assert is_valid_region(2)
    assert not is_valid_region(3)


@patch('app.mymodules.parapharmacies.df', mock_data)
def test_list_regions():
    result = list_regions()
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]['name'] == 'Region1'


@patch('app.mymodules.parapharmacies.df', mock_data)
def test_list_provinces():
    result = list_provinces(1)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]['name'] == 'Province1'


@patch('app.mymodules.parapharmacies.df', mock_data)
def test_list_cities():
    result = list_cities(1, 'Province1')
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]['name'] == 'City1'


@patch('app.mymodules.parapharmacies.df', mock_data)
def test_find_by_region_province_and_city():
    result = find_by_region_province_and_city(1, 'Province1', 'City1')
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]['name'] == 'Pharmacy1'
