import os
import requests
import pandas as pd
import polyline


class ApiError(Exception):
    """Custom exception for API handling."""
    pass


# Load API keys from environment
ORS_API_KEY = os.getenv("ORS_API_KEY")
EIA_API_KEY = os.getenv("EIA_API_KEY")


# -------------------------------------------------------------------
# 1. GET DISTANCE BETWEEN ORIGIN AND DESTINATION
# -------------------------------------------------------------------
def get_distance_miles(origin: str, destination: str) -> float:
    if ORS_API_KEY is None:
        raise ApiError("ORS_API_KEY not set in environment.")

    geo_url = "https://api.openrouteservice.org/geocode/search"
    headers = {"Authorization": ORS_API_KEY}

    # Geocode origin
    g1 = requests.get(geo_url, params={"text": origin}, headers=headers).json()
    # Geocode destination
    g2 = requests.get(geo_url, params={"text": destination}, headers=headers).json()

    try:
        o_lon, o_lat = g1["features"][0]["geometry"]["coordinates"]
        d_lon, d_lat = g2["features"][0]["geometry"]["coordinates"]
    except Exception:
        raise ApiError("Failed to geocode provided addresses.")

    # ORS directions endpoint
    directions_url = "https://api.openrouteservice.org/v2/directions/driving-car"
    body = {"coordinates": [[o_lon, o_lat], [d_lon, d_lat]]}

    r = requests.post(directions_url, json=body, headers=headers)
    data = r.json()

    try:
        meters = data["routes"][0]["summary"]["distance"]
        miles = meters / 1609.34
        return miles
    except Exception:
        raise ApiError(f"Unexpected ORS distance response: {data}")


# -------------------------------------------------------------------
# 2. GET ROUTE GEOMETRY FOR STREAMLIT MAP
# -------------------------------------------------------------------
def get_route_geometry(origin: str, destination: str):
    if ORS_API_KEY is None:
        raise ApiError("ORS_API_KEY not set in environment.")

    geo_url = "https://api.openrouteservice.org/geocode/search"
    headers = {"Authorization": ORS_API_KEY}

    # Geocode origin/destination
    g1 = requests.get(geo_url, params={"text": origin}, headers=headers).json()
    g2 = requests.get(geo_url, params={"text": destination}, headers=headers).json()

    try:
        o_lon, o_lat = g1["features"][0]["geometry"]["coordinates"]
        d_lon, d_lat = g2["features"][0]["geometry"]["coordinates"]
    except Exception:
        raise ApiError("Failed to geocode origin/destination for map.")

    # Request route geometry
    directions_url = "https://api.openrouteservice.org/v2/directions/driving-car"
    body = {"coordinates": [[o_lon, o_lat], [d_lon, d_lat]]}

    r = requests.post(directions_url, json=body, headers=headers)
    data = r.json()

    try:
        encoded_polyline = data["routes"][0]["geometry"]
    except Exception:
        raise ApiError(f"Unexpected ORS geometry response: {data}")

    # Decode encoded polyline → list of (lat, lon)
    coords = polyline.decode(encoded_polyline)

    # Convert to DataFrame for Streamlit map rendering
    df = pd.DataFrame(coords, columns=["lat", "lon"])
    return df


# -------------------------------------------------------------------
# 3. GET REAL DIESEL PRICE FROM EIA API (CORRECT SERIES)
# -------------------------------------------------------------------
def get_diesel_price() -> float:
    if EIA_API_KEY is None:
        raise ApiError("EIA_API_KEY not set in environment.")

    url = "https://api.eia.gov/v2/petroleum/pri/gnd/data/"

    params = {
        "api_key": EIA_API_KEY,
        "frequency": "weekly",
        "data[]": "value",
        "sort[0][column]": "period",
        "sort[0][direction]": "desc",
        "length": 1,

        # FACETS YOU ARE AUTHORIZED FOR:
        "facets[product][]": "EPD2D",   # No. 2 Diesel
        "facets[process][]": "PTE",     # Retail Sales
        "facets[duoarea][]": "R20"      # PADD 2 Midwest
    }

    r = requests.get(url, params=params)
    data = r.json()

    try:
        return float(data["response"]["data"][0]["value"])
    except Exception:
        raise ApiError(f"Unexpected EIA response: {data}")
