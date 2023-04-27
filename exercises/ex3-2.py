# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 13:47:19 2023

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

shopping_centres = gpd.read_file(SHOPPING_CENTERS_OUT)

# b) Create a buffer around the points
#Calculate a 1.5 km buffer for each geocoded point. Overwrite the geometry column with the new buffer geometry.
#Use the geopandas.GeoDataFrame.buffer() method, that uses shapely’s buffer() in the background. 
# You only need to care about the distance parameter, don’t worry about the possible other arguments.

shopping_centres = shopping_centres.buffer(1500)

# NON-EDITABLE CODE CELL FOR TESTING YOUR SOLUTION
assert shopping_centres.geometry.geom_type.unique() == ["Polygon"]

# there is not c?

# d) Save buffer geometry layer
shopping_centres.to_file(
    SHOPPING_CENTERS_OUT,
    layer="buffers"
)
