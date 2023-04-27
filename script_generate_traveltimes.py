# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 15:29:45 2023

@author: S.Hemminki
"""

import pathlib
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from shapely.geometry import Point

PROJECT_ROOT = pathlib.Path().resolve()
DATA_DIRECTORY = PROJECT_ROOT / "data"

METROP_ACCESS_YKR_GRID_DIR = DATA_DIRECTORY / "MetropAccess_YKR_grid"
METROP_ACCESS_YKR_GRID_FILE= METROP_ACCESS_YKR_GRID_DIR / "MetropAccess_YKR_grid_EurefFIN.shp"

TRAVEL_TIMES_TO_RAILWAY_STATION_SRC_FILE = DATA_DIRECTORY / "travel_times_to_railway_station.txt"
TRAVEL_TIMES_TO_RAILWAY_STATION_GDF_FILE = DATA_DIRECTORY / "travel_times_to_railway_station.gpkg"


def load_ykr_grid():
    ykr_grid = gpd.read_file(METROP_ACCESS_YKR_GRID_FILE)
    ykr_grid = ykr_grid.set_crs(3067, allow_override=False)
    return ykr_grid

def find_point_in_gdf(point_gdf, gdf):
    assert type(point_gdf) == gpd.GeoDataFrame
    assert type(gdf) == gpd.GeoDataFrame
    
    row_containing_point = gdf.loc[gdf.geometry.contains(point_gdf.geometry.iloc[0])]
    print(row_containing_point)
    
    return row_containing_point

def plot_multiple_gdfs(gdfs, colors=None, edgecolors=None, figsize=(10, 10)):
    # Helper method to plot multiple gdfs
    fig, ax = plt.subplots(figsize=figsize)
    
    if colors is None:
        colors = ['red'] * len(gdfs)
    
    if edgecolors is None:
        edgecolors = ['black'] * len(gdfs)
    
    for i, gdf in enumerate(gdfs):
        gdf.plot(ax=ax, color=colors[i], edgecolor=edgecolors[i])
    
    plt.show()

def get_travel_times_to_railways_station(ykr_grid):
    travel_times = pd.read_csv(TRAVEL_TIMES_TO_RAILWAY_STATION_SRC_FILE, delimiter=";")
    
    # Merge 'from_id' geometries
    travel_times = pd.merge(travel_times, ykr_grid[['YKR_ID', 'geometry']], left_on='from_id', right_on='YKR_ID')
    travel_times.drop(columns=['from_id', 'YKR_ID', 'to_id'], inplace=True)
    
    return travel_times


ykr_grid = load_ykr_grid()

railway_station = Point(24.9382, 60.1698) # Lon,lat for Hki railwaystation
railway_gdf = gpd.GeoDataFrame(geometry=[railway_station], crs='EPSG:4326')
railway_gdf_transformed = railway_gdf.to_crs(ykr_grid.crs)
plot_multiple_gdfs([ykr_grid, railway_gdf_transformed])
railway_station_grid = find_point_in_gdf(railway_gdf_transformed, ykr_grid)
railway_station_ykr_id = railway_station_grid['YKR_ID']
print(railway_station_ykr_id)

# Now that we know railway station YKR ID, load travel times to that cell 

travel_times = get_travel_times_to_railways_station(ykr_grid)
travel_times = gpd.GeoDataFrame(travel_times, crs="EPSG:3067")
travel_times.to_file(TRAVEL_TIMES_TO_RAILWAY_STATION_GDF_FILE)

