# -*- coding: utf-8 -*-
"""
Created on Tue Apr 25 16:05:55 2023

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

PROJECT_ROOT = pathlib.Path().resolve()
DATA_DIRECTORY = PROJECT_ROOT / "data"
GEOCODES_FILE = DATA_DIRECTORY / "addresses.gpkg"

ADDRESSES = [
    {'id': 1000, 'addr': 'Itämerenkatu 14, 00101 Helsinki, Finland'},
    {'id': 1001, 'addr': 'Kampinkuja 1, 00100 Helsinki, Finland'},
    {'id': 1002, 'addr': 'Kaivokatu 8, 00101 Helsinki, Finland'},
    {'id': 1003, 'addr': 'Hermannin rantatie 1, 00580 Helsinki, Finland'},
    {'id': 1005, 'addr': 'Tyynenmerenkatu 9, 00220 Helsinki, Finland'},
    {'id': 1006, 'addr': 'Mannerheimintie 5, 00100 Helsinki, Finland'},
    {'id': 1007, 'addr': 'Fredrikinkatu 61, 00100 Helsinki, Finland'},
    {'id': 1008, 'addr': 'Eteläesplanadi 2, 00130 Helsinki, Finland'},
    {'id': 1009, 'addr': 'Iso Roobertinkatu 23, 00120 Helsinki, Finland'},
    {'id': 1010, 'addr': 'Aleksanterinkatu 21, 00100 Helsinki, Finland'},
    {'id': 1011, 'addr': 'Bulevardi 1, 00120 Helsinki, Finland'},
    {'id': 1012, 'addr': 'Korkeavuorenkatu 27, 00130 Helsinki, Finland'},
    {'id': 1013, 'addr': 'Albertinkatu 36, 00180 Helsinki, Finland'},
    {'id': 1014, 'addr': 'Lönnrotinkatu 5, 00120 Helsinki, Finland'},
    {'id': 1015, 'addr': 'Pohjoisesplanadi 33, 00100 Helsinki, Finland'},
    {'id': 1016, 'addr': 'Annankatu 12, 00120 Helsinki, Finland'},
    {'id': 1017, 'addr': 'Tehtaankatu 21, 00150 Helsinki, Finland'},
    {'id': 1018, 'addr': 'Kluuvikatu 4, 00100 Helsinki, Finland'},
    {'id': 1019, 'addr': 'Punavuorenkatu 2, 00120 Helsinki, Finland'},
    {'id': 1020, 'addr': 'Kalliolanrinne 4, 00510 Helsinki, Finland'},
    {'id': 1021, 'addr': 'Malminkatu 24, 00100 Helsinki, Finland'},
    {'id': 1022, 'addr': 'Lauttasaarentie 50, 00200 Helsinki, Finland'},
    {'id': 1023, 'addr': 'Linnankoskenkatu 5, 00260 Helsinki, Finland'},
    {'id': 1024, 'addr': 'Vilhonvuorenkatu 11, 00500 Helsinki, Finland'},
    {'id': 1025, 'addr': 'Töölönkatu 51, 00250 Helsinki, Finland'}
]

WFS_KARTTA_AVOINDATA_URL = "https://kartta.hel.fi/ws/geoserver/avoindata/wfs"
WFS_HSY_KARTTA_URL = "https://kartta.hsy.fi/geoserver/wfs"


def get_geocoded_addresses(df_addresses, save_to_file=True):
    
    # check cache
    geocoded_addresses_with_id = {}
    if os.path.isfile(GEOCODES_FILE):
        # Open the file in binary mode
        print("Retrieving geocodes from cache")
        geocoded_addresses_with_id = gpd.read_file(GEOCODES_FILE)
            
    else:
        print("Retrieving geocodes from nominatim")
        geocoded_addresses = gpd.tools.geocode(
            df_addresses["addr"],
            provider="nominatim",
            user_agent="autogis2022",
            timeout=10)
        
        geocoded_addresses_with_id = geocoded_addresses.join(df_addresses)
        if save_to_file:
            geocoded_addresses.to_file(GEOCODES_FILE)
    
    gdf = gpd.GeoDataFrame(geocoded_addresses_with_id, crs="EPSG:4326")     
    
    return gdf

def transform_polygon(transformer, polygon):
    return Polygon([(transformer.transform(x, y)) for x, y in polygon.exterior.coords])


def get_feature_types_from_wfs(wfs):
    return list(wfs.contents)
    

def geo_feature_from_wfs(wfs, feature):
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

    request_url = f'{WFS_KARTTA_AVOINDATA_URL}?{url_params}'
    print(request_url)

    response = requests.get(request_url)
    replyJson = response.json()
    
    return replyJson

# Geocoding
df_addresses = pd.DataFrame(ADDRESSES)
geocoded_addresses_with_id = get_geocoded_addresses(df_addresses)

# Point-in-Polygon

# Get data from kartta.hel.fi
wfs_version = '2.0.0'
wfs = WebFeatureService(WFS_KARTTA_AVOINDATA_URL, wfs_version)

# Get feature types
feature_types = get_feature_types_from_wfs(wfs)

# Kaupungin osajako is in index 42
f_kaupungin_osajako = feature_types[42]
    
# Request feature from wfs 
replyJson = geo_feature_from_wfs(wfs, f_kaupungin_osajako)

# Project to 4326
transformer_3879_to_4326 = Transformer.from_crs("EPSG:3879", "EPSG:4326", always_xy=True)
helsinki_districts = []
helsinki_districts_dict = {'id': [], 'geometry': []}
feats = replyJson['features']
for feat in feats:
    geom_id = feat['id']
    coords = feat['geometry']['coordinates']
    poly = transform_polygon(transformer_3879_to_4326, Polygon(coords[0]))
    helsinki_districts_dict['id'].append(geom_id)
    helsinki_districts_dict['geometry'].append(poly)
    helsinki_districts.append(poly)

helsinki_districts_gdf = gpd.GeoDataFrame(helsinki_districts_dict, crs="EPSG:4326")

axes = helsinki_districts_gdf.plot()
geocoded_addresses_with_id.plot(ax=axes, color="blue", markersize=5)

point1 = Point(24.952242, 60.1696017)
point2 = Point(24.976567, 60.1612500)

point_within_any_polygon = any(point1.within(polygon) for polygon in helsinki_districts)
geocoded_addresses_with_id.within(helsinki_districts_gdf.at[0, "geometry"])


for i in range(len(helsinki_districts_gdf)):
    geom = helsinki_districts_gdf.at[i, "geometry"]
    addr_within_geom = geocoded_addresses_with_id.within(geom)
    if any(addr_within_geom):
        print('match found')
        addresses_in_district = geocoded_addresses_with_id[addr_within_geom]
        print(addresses_in_district)
        
# Intersect
line1 = LineString([(0, 0), (1, 1)])
line2 = LineString([(1, 1), (0, 2)])
MultiLineString([line1, line2])

line1.intersects(line2)

# Spatial join
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
population_grid.head()

population_grid = population_grid.to_crs(geocoded_addresses_with_id.crs)
assert geocoded_addresses_with_id.crs == population_grid.crs, "CRS are not identical"

addresses_with_population_data = geocoded_addresses_with_id.sjoin(
    population_grid,
    how="left",
    predicate="within"
)
addresses_with_population_data.head()

ax = addresses_with_population_data.plot(
    figsize=(10, 10),
    column="population_density",
    cmap="Reds",
    scheme="quantiles",
    markersize=15,
    legend=True
)
ax.set_title("Population density around address points")


ax = population_grid.plot(
    figsize=(10, 10),
    column="population_density",
    cmap="Reds",
    scheme="quantiles",
    legend=True
)
ax.set_title("Population density in the Helsinki metropolitan area")

addresses_with_population_data.to_file(
    DATA_DIRECTORY / "addresses.gpkg",
    layer="addresses_with_population_data"
)
