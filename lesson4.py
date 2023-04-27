# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 14:33:38 2023

@author: S.Hemminki
"""

import pathlib
import pandas as pd
import geopandas as gpd
from urllib.parse import urlencode
import requests
from shapely.geometry import Point, Polygon, MultiPolygon, LineString, MultiLineString
from shapely.ops import unary_union, cascaded_union
from owslib.wfs import WebFeatureService
import mapclassify
import matplotlib.pyplot as plt

PROJECT_ROOT = pathlib.Path().resolve()
DATA_DIRECTORY = PROJECT_ROOT / "data"
TRAVEL_TIMES_DIR = DATA_DIRECTORY / "travel_times_helsinki"
TRAVEL_TIMES_TO_RAILWAY_STATION_GDF_FILE = TRAVEL_TIMES_DIR / "travel_times_to_railway_station.gpkg"
TRAVEL_TIMES_LEGEND_FILE = TRAVEL_TIMES_DIR / "traveltimes_variable_legend.txt"

METROP_ACCESS_YKR_GRID_DIR = DATA_DIRECTORY / "MetropAccess_YKR_grid"
METROP_ACCESS_YKR_GRID_FILE= METROP_ACCESS_YKR_GRID_DIR / "MetropAccess_YKR_grid_EurefFIN.shp"

AMAZON_RIVER_DIR = DATA_DIRECTORY / "amazon_river"
AMAZON_RIVER_SHP_FILE = AMAZON_RIVER_DIR / "amzmainstm_v.shp"

WFS_HEL_KARTTA_URL = "https://kartta.hel.fi/ws/geoserver/avoindata/wfs"
WFS_HSY_KARTTA_URL = "https://kartta.hsy.fi/geoserver/wfs"


def load_travel_times_to_railway_station():
    return gpd.read_file(TRAVEL_TIMES_TO_RAILWAY_STATION_GDF_FILE)
    
def get_feature_types_from_wfs(wfs):
    return list(wfs.contents)
    
def geo_feature_from_wfs(baseurl, wfs, feature):
    # Define the WFS request parameters
    params = {
        'service': 'wfs',
        'request': 'getFeature',
        'typename': feature,
        'outputFormat': 'application/json'
    }
    
    url_params = urlencode(params)
    # Replace %2C with comma and %3A with colon
    for key, value in params.items():
        url_params = url_params.replace('%2C', ',').replace('%3A', ':')

    request_url = f'{baseurl}?{url_params}'
    print(request_url)

    response = requests.get(request_url)
    replyJson = response.json()
    
    return replyJson

def replyJson_to_gdf(replyJson, crs):
    reply_dict = {'id': [], 'geometry': []}
    feats = replyJson['features']
    for feat in feats:
        geom_id = feat['id']
        coords = feat['geometry']['coordinates']
        poly = Polygon(coords[0])
        reply_dict['id'].append(geom_id)
        reply_dict['geometry'].append(poly)
        
    gdf = gpd.GeoDataFrame(reply_dict, crs=crs)
    return gdf

def load_ykr_grid():
    ykr_grid = gpd.read_file(METROP_ACCESS_YKR_GRID_FILE)
    ykr_grid = ykr_grid.set_crs(3067, allow_override=False)
    return ykr_grid

def get_gdf_outline(gdf):
    assert type(gdf) == gpd.GeoDataFrame, "input must be of type GeoDataFrame"
    combined_geometry = unary_union(gdf['geometry'])
    outline = combined_geometry.boundary
    # Merge the MultiLineString into a single LineString
    merged_linestring = cascaded_union(outline)
    convex_hull_polygon = merged_linestring.convex_hull 
    gdf_convex_hull = gpd.GeoDataFrame(geometry=[convex_hull_polygon], crs=gdf.crs)

    return gdf_convex_hull  

# Overlay analysis

# Load travel times to railways station as YKR Grid
travel_times_rws = load_travel_times_to_railway_station()

# Load map to variable - legend
travel_times_var_legend = pd.read_csv(TRAVEL_TIMES_LEGEND_FILE)

# Get data from kartta.hel.fi
wfs_version = '2.0.0'

# Get feature types
wfs_hel = WebFeatureService(WFS_HEL_KARTTA_URL, wfs_version)
wfs_hsy = WebFeatureService(WFS_HSY_KARTTA_URL, wfs_version)

feature_types_kartta_hsy = get_feature_types_from_wfs(wfs_hsy)
feature_types_kartta_hel = get_feature_types_from_wfs(wfs_hel)

# replyJson = geo_feature_from_wfs(WFS_HEL_KARTTA_URL, wfs_hel, "avoindata:Seutukartta_aluejako_kuntarajat")
replyJson = geo_feature_from_wfs(WFS_HEL_KARTTA_URL, wfs_hel, feature_types_kartta_hel[42])

helsinki_municipality_gdf = replyJson_to_gdf(replyJson, "EPSG:3879") 
helsinki_municipality_outline = get_gdf_outline(helsinki_municipality_gdf)
helsinki_municipality_outline = helsinki_municipality_outline.to_crs(travel_times_rws.crs)

intersection = travel_times_rws.overlay(helsinki_municipality_outline, how="intersection")

intersection.to_file(
    DATA_DIRECTORY / "intersection.gpkg",
    layer="travel_time_matrix_helsinki_region"
)

# Aggregating data

# Conduct the aggregation
dissolved = intersection.dissolve(by="car_r_t")

print(f"Rows in original intersection GeoDataFrame: {len(intersection)}")
print(f"Rows in dissolved layer: {len(dissolved)}")

# Select only geometries that are within 15 minutes away
dissolved_loc15 = dissolved.loc[15]

# Create a GeoDataFrame
selection = gpd.GeoDataFrame([dissolved_loc15], crs=dissolved.crs)
selection.plot()

# Reset index
dissolved = dissolved.reset_index()
dissolved.plot(column="car_r_t")

# Simplifying geometries

# Load amazon river shape
amazon_river = gpd.read_file(AMAZON_RIVER_SHP_FILE)
amazon = MultiLineString(amazon_river['geometry'].tolist())
amazon_gdf = gpd.GeoDataFrame(index=[0], crs=amazon_river.crs, geometry=[amazon])
amazon_gdf = amazon_gdf.to_crs('epsg:3857')

# Generalize geometry
amazon_gdf['simplegeom'] = amazon_gdf.simplify(tolerance=20000)
# Set geometry to be our new simlified geometry
amazon_gdf = amazon_gdf.set_geometry('simplegeom')

# Plot 
amazon_gdf.plot()

# Reclassifying data
# Include only data that is above or equal to 0
accessibility_grid = travel_times_rws
accessibility_grid = accessibility_grid.loc[accessibility_grid["pt_r_tt"] >=0]

# Plot using 15 classes and classify the values using "Natural Breaks" classification
accessibility_grid.plot(column="pt_r_tt", scheme="Natural_Breaks", k=15, cmap="RdYlBu", linewidth=0, legend=True)

# Plot walking distance
accessibility_grid.plot(column="walk_d", scheme="Natural_Breaks", k=15, cmap="RdYlBu", linewidth=0, legend=True)

mapclassify.NaturalBreaks(y=accessibility_grid["pt_r_tt"], k=15)
mapclassify.Quantiles(y=accessibility_grid["pt_r_tt"])
classifier = mapclassify.NaturalBreaks(y=accessibility_grid["pt_r_tt"], k=15)

# Create a Natural Breaks classifier
classifier = mapclassify.NaturalBreaks.make(k=15)
# Classify the data
classifications = accessibility_grid[["pt_r_tt"]].apply(classifier)

# Let's see what we have
classifications.head()

# Rename the column so that we know that it was classified with natural breaks
accessibility_grid["nb_pt_r_tt"] = accessibility_grid[["pt_r_tt"]].apply(classifier)

# Check the original values and classification
accessibility_grid[["pt_r_tt", "nb_pt_r_tt"]].head()

# Plot
accessibility_grid.plot(column="nb_pt_r_tt", linewidth=0, legend=True)

# Histogram for public transport rush hour travel time
accessibility_grid["pt_r_tt"].plot.hist(bins=50)

# Define classifier
classifier = mapclassify.NaturalBreaks(y=accessibility_grid["pt_r_tt"], k=9)

# Plot histogram for public transport rush hour travel time
accessibility_grid["pt_r_tt"].plot.hist(bins=50)

# Add vertical lines for class breaks
for break_point in classifier.bins:
    plt.axvline(break_point, color="k", linestyle="dashed", linewidth=1)
    
# Let’s do our classification based on two criteria: and find out grid cells
# Grid cells where the travel time is lower or equal to 20 minutes
# and they are further away than 4 km (4000 meters) from the city center.
accessibility_grid.iloc[0]["pt_r_tt"] < 20 and accessibility_grid.iloc[0]["walk_d"] > 4000
int(accessibility_grid.iloc[11293]["pt_r_tt"] < 20 and accessibility_grid.iloc[11293]["walk_d"] > 4000)


accessibility_grid["suitable_area"] = accessibility_grid.apply(lambda row: int(row["pt_r_tt"] < 20 and row["walk_d"] > 4000), axis=1)
# Get value counts
accessibility_grid["suitable_area"].value_counts()
# Plot
accessibility_grid.plot(column="suitable_area", linewidth=0)

