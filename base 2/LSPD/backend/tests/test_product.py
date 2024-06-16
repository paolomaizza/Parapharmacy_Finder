import pytest
import pandas as pd
from unittest.mock import patch
from app.product import get_product_details, print_product_details

# Mock data
mock_data = pd.DataFrame({
    'COMMERCIAL_CODE': ['123', '456', '789'],
    'NAME_PRODUCT': [
        '"VALID_PRODUCT description1"',
        '"OTHER_PRODUCT description2"',
        '"VALID_PRODUCT description3"'
    ]
})

mock_data_no_name_product = pd.DataFrame({
    'COMMERCIAL_CODE': ['123', '456', '789']
})

mock_data_with_other_product = pd.DataFrame({
    'COMMERCIAL_CODE': ['123', '456', '789'],
    'NAME_PRODUCT': [
        '"TACHIPIRINA description1"',
        '"OTHER_PRODUCT description2"',
        '"TACHIPIRINA description3"'
    ]
})


@patch('app.product.products_df', mock_data)
def test_get_product_details():
    product_details = get_product_details()
    assert isinstance(product_details, dict), (
        "The returned product details should be a dictionary"
    )
    assert "VALID_PRODUCT" in product_details, (
        "VALID_PRODUCT should be in the product details"
    )
    assert len(product_details["VALID_PRODUCT"]) == 2, (
        "There should be two entries for VALID_PRODUCT"
    )


@patch('app.product.products_df', mock_data)
def test_print_product_details(capsys):
    print_product_details()
    captured = capsys.readouterr()
    assert "Product: VALID_PRODUCT" in captured.out, (
        "The output should contain 'Product: VALID_PRODUCT'"
    )


@patch('app.product.products_df', mock_data_no_name_product)
def test_get_product_details_no_name_product():
    product_details = get_product_details()
    assert product_details == {}, (
        "The product details should be an empty dictionary if "
        "NAME_PRODUCT column is missing"
    )


@patch('app.product.products_df', mock_data_no_name_product)
def test_print_product_details_no_name_product(capsys):
    print_product_details()
    captured = capsys.readouterr()
    assert (
        "The column 'NAME_PRODUCT' does not exist in the CSV file."
    ) in captured.out, "The output should contain the missing column warning"


@patch('app.product.products_df', mock_data)
def test_search_product_found():
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    response = client.get("/search-product?product_name=VALID_PRODUCT")
    assert response.status_code == 200
    assert "product" in response.json()
    assert response.json()["product"] == "VALID_PRODUCT"


@patch('app.product.products_df', mock_data)
def test_search_product_not_found():
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    response = client.get("/search-product?product_name=NON_EXISTENT_PRODUCT")
    assert response.status_code == 404
    assert response.json() == {
        "detail": (
            "The product 'NON_EXISTENT_PRODUCT' is not available "
            "in the pharmacy."
        )
    }


def test_csv_reading_error(capsys):
    with patch('app.product.pd.read_csv', side_effect=pd.errors.ParserError(
            "Error parsing CSV")):
        # Re-import the module to re-trigger the import block execution
        import importlib
        import app.product
        importlib.reload(app.product)
        captured = capsys.readouterr()
        assert "Error reading the CSV file:" in captured.out, (
            "The output should contain the CSV error message"
        )
        assert app.product.products_df.empty, (
            "The DataFrame should be empty if there is a CSV parsing error"
        )


@patch('app.product.products_df', mock_data_with_other_product)
def test_main_block(capsys):
    from app.product import print_product_details
    with patch('app.product.__name__', "__main__"):
        with patch('app.product.__file__', "app/product.py"):
            print_product_details()
            captured = capsys.readouterr()
            assert "Product: TACHIPIRINA" in captured.out, (
                "The output should contain 'Product: TACHIPIRINA'"
            )
