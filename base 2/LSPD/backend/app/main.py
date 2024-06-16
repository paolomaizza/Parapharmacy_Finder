from datetime import datetime
from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from .mymodules.parapharmacies import (
    find_by_region,
    is_valid_region,
    list_regions,
    list_provinces,
    list_cities,
    find_by_region_province_and_city
)
from .product import get_product_details
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get('/')
def read_root():
    return {"Hello": "World"}


@app.get('/query/{region}')
def read_item(region: str):
    try:
        region = int(region)
    except ValueError:
        return {"error": "Invalid format. Expecting a numeric region code"}
    if is_valid_region(region):
        return {"region": region, "parapharmacies": find_by_region(region)}
    else:
        return {"error": f"Invalid region code {region}"}


@app.get('/get-date')
def get_date():
    current_date = datetime.now().isoformat()
    return JSONResponse(content={"date": current_date})


@app.get('/regions')
def get_regions():
    return {"regions": list_regions()}


@app.get('/regions/{region_code}/provinces')
def get_provinces(region_code: int):
    return {"provinces": list_provinces(region_code)}


@app.get('/regions/{region_code}/provinces/{province_name}/cities')
def get_cities(region_code: int, province_name: str):
    return {"cities": list_cities(region_code, province_name)}


@app.get(
    '/regions/{region_code}/provinces/{province_name}/cities/{city_name}/'
    'pharmacies'
)
def get_pharmacies(region_code: int, province_name: str, city_name: str):
    return {
        "pharmacies": find_by_region_province_and_city(
            region_code, province_name, city_name
        )
    }


@app.get('/search-product')
def search_product(
    product_name: str = Query(
        ..., description="Name of the product to search"
    )
):
    product_details = get_product_details()
    product_name = product_name.strip().upper()
    if product_name in product_details:
        return {
            "product": product_name,
            "details": product_details[product_name]
        }
    else:
        raise HTTPException(
            status_code=404,
            detail=(
                f"The product '{product_name}' is not available "
                "in the pharmacy."
            )
        )
