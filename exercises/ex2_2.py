# -*- coding: utf-8 -*-
"""
Created on Thu Apr 20 07:58:37 2023

@author: S.Hemminki
"""

from shapely.geometry import Polygon
from shapely.geometry import Point
import geopandas as gpd
import pandas as pd
import pathlib

EXERCISE_FOLDER = pathlib.Path().resolve()
ROOT_FOLDER = EXERCISE_FOLDER.parent.resolve()
DATA_DIRECTORY = ROOT_FOLDER / "data"


data = pd.read_csv(DATA_DIRECTORY / "some_posts.csv")

print(f"Number of rows: {len(data)}")

data["geometry"] = None
points = data.apply(lambda row: Point(row["lon"], row["lat"]), axis=1)
data["geometry"] = points
    
gdata = gpd.GeoDataFrame(data, crs="EPSG:4326")
gdata.to_file(DATA_DIRECTORY / "kruger_points.shp")