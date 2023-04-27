# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 09:39:05 2023

@author: S.Hemminki
"""

import pathlib
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import mapclassify as mc

EXERCISES_DIR = pathlib.Path().resolve()
EXERCISES_DATA_DIR = EXERCISES_DIR / "ex4_data"
PROJECT_ROOT = EXERCISES_DIR.parent.resolve()
DATA_DIRECTORY = PROJECT_ROOT / "data"
TRAVEL_TIMES_DIR = EXERCISES_DIR / "ex4_data"
METROP_ACCESS_YKR_GRID_DIR = DATA_DIRECTORY / "MetropAccess_YKR_grid"
METROP_ACCESS_YKR_GRID_FILE= METROP_ACCESS_YKR_GRID_DIR / "MetropAccess_YKR_grid_EurefFIN.shp"

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
            df = pd.read_csv(filepath, delimiter=";", usecols=['from_id', 'to_id', 'pt_r_t', 'car_r_t'])
            df = df.loc[df["pt_r_t"] >=0]
            df = df.loc[df["car_r_t"] >=0]
            dataframes[dataframe_name] = df
            
    return dataframes


# a) Read the grid cell data set
grid = load_ykr_grid()

# b) Read the travel time data sets and join them to the grid cells
travel_times = read_txt_files(EXERCISES_DATA_DIR)

tt_jumbo = travel_times["travel_times_to_5878070_Jumbo"]
tt_itis = travel_times["travel_times_to_5944003_Itis"]
tt_dixi = travel_times["travel_times_to_5878087_Dixi"]
tt_myyrmanni = travel_times["travel_times_to_5902043_Myyrmanni"]
tt_forum = travel_times["travel_times_to_5975373_Forum"]
tt_omena = travel_times["travel_times_to_5978593_Iso_Omena"]
tt_ruoholahti = travel_times["travel_times_to_5980260_Ruoholahti"]

# Join
grid = (
    grid.set_index("YKR_ID")
    .join(tt_itis.set_index('from_id').add_suffix("_Itis"))
    .drop('to_id_Itis', axis=1)
    .join(tt_myyrmanni.set_index('from_id').add_suffix("_Myyrmanni"))
    .drop('to_id_Myyrmanni', axis=1)
)

# NON-EDITABLE TEST CELL
assert type(grid) == gpd.geodataframe.GeoDataFrame, "Output should be a geodataframe."

required_columns = ['pt_r_t_Itis', 'car_r_t_Itis', 'pt_r_t_Myyrmanni', 'car_r_t_Myyrmanni', 'geometry']
assert all(column in grid.columns for column in required_columns), "Couldn’t find all required columns."

for shopping_centre in ("Itis", "Myyrmanni"):
    for column in ("car_r_t", "pt_r_t"):
        assert -1 not in grid[f"{column}_{shopping_centre}"], "NoData values (-1) should be removed from the data!"

# c) Classify the travel times into five-minute intervals
class_breaks = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]
for mode in ['pt_r_t_Itis', 'car_r_t_Itis', 'car_r_t_Myyrmanni', 'pt_r_t_Myyrmanni']:
    classifier = mc.UserDefined(y=grid[mode], bins=class_breaks)
    grid[mode.replace('r_t_', 'r_t_cl_')] = grid[mode].apply(classifier)

# NON-EDITABLE TEST CELL
# Check the output
print("travel times by public transport:")
grid[['pt_r_t_Itis', 'pt_r_t_cl_Itis']].head()

# NON-EDITABLE TEST CELL
# Check the output
print("Travel times by car:")
grid[["car_r_t_Myyrmanni", "car_r_t_cl_Myyrmanni"]].head()


# d) Plot the classified travel times
fig, axs = plt.subplots(nrows=2, ncols=2, figsize=(10, 10))

titles = {
    "pt_r_t_cl_Itis": "Public Transport Travel Times to Itis",
    "car_r_t_cl_Itis": "Car Travel Times to Itis",
    "pt_r_t_cl_Myyrmanni": "Public Transport Travel Times to Myyrmanni",
    "car_r_t_cl_Myyrmanni": "Car Travel Times to Myyrmanni"
}

# Loop through the modes and destinations, and plot each classified travel time column
for i, mode in enumerate(['pt_r_t_cl_', 'car_r_t_cl_']):
    for j, dest in enumerate(['Itis', 'Myyrmanni']):
        colname = mode + dest
        axs[i,j].set_title(titles[colname])
        grid[colname].value_counts().sort_index().plot(kind="bar", ax=axs[i,j])
        
# Adjust the layout and spacing
fig.tight_layout(pad=3.0)

fig.savefig(EXERCISES_DATA_DIR / 'tt_to_shopping_centers.png')