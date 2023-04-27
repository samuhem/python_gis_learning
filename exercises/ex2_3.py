# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 07:58:37 2023

@author: S.Hemminki
"""

from shapely.geometry import Polygon
from shapely.geometry import Point
from shapely.geometry import LineString
import geopandas as gpd
import pathlib
import pyproj
import numpy as np

EXERCISE_FOLDER = pathlib.Path().resolve()
ROOT_FOLDER = EXERCISE_FOLDER.parent.resolve()
DATA_DIRECTORY = ROOT_FOLDER / "data"

kruger_points = gpd.read_file(DATA_DIRECTORY / "kruger_points.shp")

kp_projected = kruger_points.to_crs("EPSG:32735")
assert kp_projected.crs == pyproj.CRS("EPSG:32735")

grouped_by_users = kp_projected.groupby("userid")
assert len(grouped_by_users.groups) == kruger_points["userid"].nunique(), "Number of groups should match number of unique users!"

movements_dict = {'user': [], 'geometry': []}
for user, data in grouped_by_users:
    if len(data) < 2:
        continue
    data_sorted = data.sort_values(by='timestamp', ascending=True)
    path = LineString(data_sorted['geometry'])
    movements_dict['user'].append(user)
    movements_dict['geometry'].append(path)
    
movements = gpd.GeoDataFrame(movements_dict, crs="EPSG:32735")

shortest_distance = np.min(movements.length)
mean_distance = np.mean(movements.length)
longest_distance = np.max(movements.length)

movements.to_file(DATA_DIRECTORY / "movements.shp")