# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 11:07:53 2023

@author: S.Hemminki
"""

import pathlib
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import mapclassify as mc
from enum import Enum

EXERCISES_DIR = pathlib.Path().resolve()
EXERCISES_DATA_DIR = EXERCISES_DIR / "ex4_data"
PROJECT_ROOT = EXERCISES_DIR.parent.resolve()
DATA_DIRECTORY = PROJECT_ROOT / "data"
TRAVEL_TIMES_DIR = EXERCISES_DIR / "ex4_data"
METROP_ACCESS_YKR_GRID_DIR = DATA_DIRECTORY / "MetropAccess_YKR_grid"
METROP_ACCESS_YKR_GRID_FILE= METROP_ACCESS_YKR_GRID_DIR / "MetropAccess_YKR_grid_EurefFc

def load_ykr_grid():
    ykr_grid = gpd.read_file(METROP_ACCESS_YKR_GRID_FILE)
    ykr_grid = ykr_grid.set_crs(3067)
    return ykr_grid

def read_txt_files(directory):
    dataframes = {}
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            filepath = os.path.join(directory, filename)
            dataframe_name = os.path.splitext(filename)[0]
            df = pd.read_csv(filepath, delimiter=";", usecols=['from_id', 'to_id', 'car_r_t'])
            df = df.loc[df["car_r_t"] >=0]
            dataframes[dataframe_name] = df
            
    return dataframes


# Read the grid cell data set
grid = load_ykr_grid()

# Read the travel time data sets and join them to the grid cells
travel_times = read_txt_files(EXERCISES_DATA_DIR)

tt_itis = travel_times["travel_times_to_5944003_Itis"]
tt_dixi = travel_times["travel_times_to_5878087_Dixi"]
tt_myyrmanni = travel_times["travel_times_to_5902043_Myyrmanni"]
tt_forum = travel_times["travel_times_to_5975373_Forum"]
tt_omena = travel_times["travel_times_to_5978593_Iso_Omena"]
tt_ruoholahti = travel_times["travel_times_to_5980260_Ruoholahti"]
tt_jumbo = travel_times["travel_times_to_5878070_Jumbo"]

# Join
grid = (
    grid.set_index("YKR_ID")
    .join(tt_itis.set_index('from_id').add_suffix("_Itis"))
    .drop('to_id_Itis', axis=1)
    .join(tt_myyrmanni.set_index('from_id').add_suffix("_Myyrmanni"))
    .drop('to_id_Myyrmanni', axis=1)
    .join(tt_dixi.set_index('from_id').add_suffix("_Dixi"))
    .drop('to_id_Dixi', axis=1)
    .join(tt_forum.set_index('from_id').add_suffix("_Forum"))
    .drop('to_id_Forum', axis=1)
    .join(tt_omena.set_index('from_id').add_suffix("_Omena"))
    .drop('to_id_Omena', axis=1)
    .join(tt_ruoholahti.set_index('from_id').add_suffix("_Ruoholahti"))
    .drop('to_id_Ruoholahti', axis=1)
    .join(tt_jumbo.set_index('from_id').add_suffix("_Jumbo"))
    .drop('to_id_Jumbo', axis=1)
)

# For each row in grid, find closest by car_r_t
car_r_cols = ['car_r_t_Itis', 'car_r_t_Myyrmanni', 'car_r_t_Dixi', 'car_r_t_Forum', 'car_r_t_Omena', 'car_r_t_Ruoholahti', 'car_r_t_Jumbo']
grid['closest_sc'] = grid[car_r_cols].idxmin(axis=1)
grid['closest_d'] = grid[car_r_cols].min(axis=1)

# Visualise dominance areas
fig, axs = plt.subplots(nrows=1, ncols=2, figsize=(20, 10))
titles = ["Most Dominant Shopping Centre", "Travel Time to Closest Shopping Centre"]

# Plot dominance
grid.plot(column='closest_sc', ax=axs[0], cmap='Dark2', legend=True)
axs[0].set_title(titles[0])

# Plot travel times
grid.plot(column='closest_d', ax=axs[1], cmap='hot', legend=True)
axs[1].set_title(titles[1])

# Save to file
plt.savefig(EXERCISES_DATA_DIR / 'dominance.png')