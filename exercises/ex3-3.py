# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 14:00:22 2023

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

# a) Load the population grid data set and the buffer geometries
# Use the same population grid data set as during lesson 3 (load it directly from WFS, don’t forget to assign a CRS).
# Load the data into a GeoDataFrame called population_grid.
# (optional) If you want, discard unneeded columns and translate the remaining column names from Finnish to English.

def get_population_grid():
    population_grid = gpd.read_file(
        (
            "https://kartta.hsy.fi/geoserver/wfs"
            "?service=wfs"
            "&version=2.0.0"
            "&request=GetFeature"
            "&typeName=asuminen_ja_maankaytto:Vaestotietoruudukko_2021"
            "&srsName=EPSG:3879"
        ),
    )
    population_grid.crs = crs="EPSG:3879" 
    
    population_grid = population_grid[["asukkaita", "geometry"]]
    population_grid = population_grid.rename(columns={"asukkaita": "population"})
    
    population_grid["population_density"] = (
        population_grid["population"]
        / (population_grid.area / 1_000_000)
    )
    
    # NON-EDITABLE CODE CELL FOR TESTING YOUR SOLUTION
    assert isinstance(population_grid, gpd.GeoDataFrame)
    assert population_grid.crs == pyproj.CRS("EPSG:3879")
    
    return population_grid

def get_shopping_centers_with_buffer():
    # Read the specific layer and all layers from the GeoPackage file
    shopping_centres_buffer_layer = gpd.read_file(SHOPPING_CENTERS_OUT, layer="buffers")
    shopping_centres_buffers = gpd.read_file(SHOPPING_CENTERS_OUT, layer=None)
    # Create a GeoDataFrame using the geometry from the specific layer
    shopping_centres_buffers = gpd.GeoDataFrame(shopping_centres_buffers, geometry=shopping_centres_buffer_layer.geometry)

    # NON-EDITABLE CODE CELL FOR TESTING YOUR SOLUTION
    assert isinstance(shopping_centres_buffers, gpd.GeoDataFrame)
    assert shopping_centres_buffers.geometry.geom_type.unique() == ["Polygon"]
    assert shopping_centres_buffers.crs == pyproj.CRS("EPSG:3879")
    
    return shopping_centres_buffers
    


population_grid = get_population_grid()
shopping_centres_buffers = get_shopping_centers_with_buffer()

# b) Carry out a spatial join between the population_grid and the shopping_centre_buffers
# Join the shopping centre’s id column (and others, if you want) to the population grid data frame, 
# for all population grid cells that are within the buffer area of each shopping centre. 
# Use a join-type that retains only rows from both input data frames for which the geometric predicate is true. 
shopping_centers_with_population = gpd.sjoin(
    population_grid, 
    shopping_centres_buffers,
    how="inner",
    predicate="within"
)

shopping_centers_with_population = shopping_centers_with_population[
    ['id','name','addr','population','population_density','geometry']]

# c) Compute the population sum around shopping centres
# Group the resulting (joint) data frame by shopping centre (id or name), 
# and calculate the sum() of the population living inside the 1.5 km radius around them.
# Print the results, for instance, in the form "12345 people live within 1.5 km from REDI".
shopping_centers_with_population_grouped = shopping_centers_with_population.groupby("name")
for shopping_center_name, group_data in shopping_centers_with_population_grouped:
    popsum = group_data['population'].sum()
    print(f'Shopping center: {shopping_center_name}')
    print(f'population sum: {popsum}')



# d) Reflection

# Good job! You are almost done with this week’s exercise. Please quickly answer the following short questions:

#    How challenging did you find problems 1-3 (on scale to 1-5), and why?
#    What was easy?
#    What was difficult?

# Add your answers in a new Markdown cell below: