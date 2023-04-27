# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 13:30:53 2023

@author: S.Hemminki
"""

import pathlib
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from pyproj import Transformer
from urllib.parse import urlencode
import requests
from shapely.geometry import Point, Polygon, MultiPolygon, LineString, MultiLineString
from shapely.ops import transform
from owslib.wfs import WebFeatureService
import os
import sys
import pyproj

PROJECT_ROOT = pathlib.Path().resolve()
SHOPPING_CENTERS_SRC = PROJECT_ROOT / "shopping_centers.txt"
SHOPPING_CENTERS_OUT = PROJECT_ROOT / "shopping_centers.gpkg"

# b) Read the list of addresses

# Import shopping-centers.txt
columns = ['id', 'name', 'addr']
shopping_centers = pd.read_csv(SHOPPING_CENTERS_SRC, delimiter=";", header=None, names=columns)

import pandas
assert isinstance(shopping_centers, pandas.DataFrame)
for column in ("id", "name", "addr"):
    assert column in shopping_centers.columns
    
    
    
    
# c) Geocode the addresses
geocoded_addresses = gpd.tools.geocode(
    shopping_centers["addr"],
    provider="nominatim",
    user_agent="autogis2022",
    timeout=10)

geocoded_addresses.join(shopping_centers)
shopping_centers = shopping_centers.join(geocoded_addresses)
shopping_centers = gpd.GeoDataFrame(shopping_centers, crs="EPSG:4326")


# NON-EDITABLE CODE CELL FOR TESTING YOUR SOLUTION
import geopandas
assert isinstance(shopping_centers, geopandas.GeoDataFrame)
for column in ("id", "name", "addr", "geometry"):
    assert column in shopping_centers.columns
    
shopping_centers = shopping_centers.to_crs("EPSG:3879") 
assert shopping_centers.crs == pyproj.CRS("EPSG:3879")

# d) Save the resulting vector data set
shopping_centers.to_file(SHOPPING_CENTERS_OUT)