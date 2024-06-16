"""
Python interface to the `parafarmacie.csv` dataset.

This module defines a simple set of API to retrieve
data from the `parafarmacie.csv` data.
"""
import os
import pandas as pd

df = pd.read_csv(
    os.path.join(
        os.path.dirname(__file__),
        os.path.pardir,
        'parafarmacie.csv'
    ),
    delimiter=';'
)


def find_by_region(region: int):
    """
    Returns the list of parapharmacies in the
    specified region.

    Args:
        region (int): The code of the region.

    Returns:
        list: JSON-encoded parapharmacies in the selected region.
    """
    result = df[(df["CODICEREGIONE"] == int(region))]
    result.sort_values(
        by=["DESCRIZIONECOMUNE", "DENOMINAZIONESITO"],
        inplace=True,
        key=lambda col: col.str.lower()
    )
    return [
        {
            "name": row["DENOMINAZIONESITO"],
            "address": row["INDIRIZZO"],
            "cap": row["CAP"],
            "city": row["DESCRIZIONECOMUNE"],
        }
        for _, row in result.iterrows()
    ]


def is_valid_region(region: int):
    """
    Check if a region code corresponds to a valid region
    in the dataset.

    Args:
        region (int):  The code of the region.

    Returns:
        bool: True if the region code is valid, False otherwise.
    """
    return region in [r["code"] for r in list_regions()]


def list_regions():
    """
    Returns the list of available regions in code/name format.

    Returns:
        list: JSON-encoded regions in code/name format.
    """
    regions = df[["CODICEREGIONE", "DESCRIZIONEREGIONE"]].drop_duplicates()
    regions.sort_values(by="DESCRIZIONEREGIONE", inplace=True)
    return [
        {
            "code": row["CODICEREGIONE"],
            "name": row["DESCRIZIONEREGIONE"],
        }
        for _, row in regions.iterrows()
    ]


def list_provinces(region: int):
    """
    Returns the list of available provinces in the specified region.

    Args:
        region (int): The code of the region.

    Returns:
        list: JSON-encoded provinces in the selected region.
    """
    provinces = df[df["CODICEREGIONE"] == region][
        ["DESCRIZIONEPROVINCIA"]
    ].drop_duplicates()
    provinces.sort_values(by="DESCRIZIONEPROVINCIA", inplace=True)
    return [
        {
            "name": row["DESCRIZIONEPROVINCIA"],
        }
        for _, row in provinces.iterrows()
    ]


def list_cities(region: int, province: str):
    """
    Returns the list of available cities in the specified region and province.

    Args:
        region (int): The code of the region.
        province (str): The name of the province.

    Returns:
        list: JSON-encoded cities in the selected region and province.
    """
    cities = df[
        (df["CODICEREGIONE"] == region) &
        (df["DESCRIZIONEPROVINCIA"].str.lower() == province.lower())
    ][["DESCRIZIONECOMUNE"]].drop_duplicates()
    cities.sort_values(by="DESCRIZIONECOMUNE", inplace=True)
    return [
        {
            "name": row["DESCRIZIONECOMUNE"],
        }
        for _, row in cities.iterrows()
    ]


def find_by_region_province_and_city(region: int, province: str, city: str):
    """
    Returns the list of parapharmacies in the specified region,
    province, and city.

    Args:
        region (int): The code of the region.
        province (str): The name of the province.
        city (str): The name of the city.

    Returns:
        list: JSON-encoded parapharmacies in the selected region,
              province, and city.
    """
    result = df[
        (df["CODICEREGIONE"] == region) &
        (df["DESCRIZIONEPROVINCIA"].str.lower() == province.lower()) &
        (df["DESCRIZIONECOMUNE"].str.lower() == city.lower())
    ]
    result.sort_values(
        by=["DESCRIZIONECOMUNE", "DENOMINAZIONESITO"],
        inplace=True,
        key=lambda col: col.str.lower()
    )
    return [
        {
            "name": row["DENOMINAZIONESITO"],
            "address": row["INDIRIZZO"],
            "cap": row["CAP"],
            "city": row["DESCRIZIONECOMUNE"],
        }
        for _, row in result.iterrows()
    ]
