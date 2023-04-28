# -*- coding: utf-8 -*-
"""
Created on Fri Apr 28 09:47:27 2023

@author: S.Hemminki
"""

import pathlib
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import os
import mapclassify as mc
import folium
import webbrowser
import json
import branca.colormap as cm

EXERCISES_DIR = pathlib.Path().resolve()
EXERCISES_DATA_DIR = EXERCISES_DIR / "ex5_data"
PROJECT_ROOT = EXERCISES_DIR.parent.resolve()
DATA_DIRECTORY = PROJECT_ROOT / "data"
TRAVEL_TIMES_DIR = EXERCISES_DIR / "ex4_data"
METROP_ACCESS_YKR_GRID_DIR = DATA_DIRECTORY / "MetropAccess_YKR_grid"
METROP_ACCESS_YKR_GRID_FILE= METROP_ACCESS_YKR_GRID_DIR / "MetropAccess_YKR_grid_EurefFIN.shp"

TRAVEL_TIMES_BASE_DIR = "D:\\Data\\HelsinkiTravelTimes\\HelsinkiTravelTimeMatrix2018\\"
TRAVEL_TIMES_FILES_PREFFIX = "travel_times_to_ "

# Ex 1 & 2: Show difference between pt time & car travel time to selected grid cell
# CO2? Ticket price vs fuel price?

def get_first_digits(number, n_digits):
    assert type(number) == int, "Input number should be of type int"
    assert type(n_digits) == int, "Input n_digits should be of type int"
    return int(str(number)[:n_digits])


def find_directory_starting_with(target_folder, digits):
    # List all entries in the target folder
    entries = os.listdir(target_folder)

    # Filter only directories
    directories = [entry for entry in entries if os.path.isdir(os.path.join(target_folder, entry))]

    # Find the directory with the name starting with the specified digits
    for directory in directories:
        if directory.startswith(str(digits)):
            return directory

    # If no matching directory is found, return None
    return None

def find_file_matching_number(directory, number):
    # List all entries in the directory
    entries = os.listdir(directory)

    # Filter only files
    files = [entry for entry in entries if os.path.isfile(os.path.join(directory, entry))]

    # Find the file with the name matching the specified number
    for file in files:
        file_name, _ = os.path.splitext(file)
        if file_name == str(number):
            return file

    # If no matching file is found, return None
    return None

def format_dir_name(seven_digit_number):
    assert isinstance(seven_digit_number, int), "Input must be an integer."
    assert 1000000 <= seven_digit_number <= 9999999, "Input must be a 7-digit number."

    first_four_digits = str(seven_digit_number)[:4]
    result = first_four_digits + 'xxx'
    return result

def save_and_open_map(mymap):
    assert type(mymap) == folium.Map, "Input mymap should be folium.Map"
    if not os.path.exists(EXERCISES_DATA_DIR):
        os.makedirs(EXERCISES_DATA_DIR)
    mymap.save(EXERCISES_DATA_DIR / "interactive_map.html")
    webbrowser.open_new_tab(EXERCISES_DATA_DIR / "interactive_map.html")
    
def load_ykr_grid():
    ykr_grid = gpd.read_file(METROP_ACCESS_YKR_GRID_FILE)
    ykr_grid = ykr_grid.set_crs(3067)
    return ykr_grid

def load_traveltimes_to_grid_cell(cell_id):
    assert type(cell_id) == int, "Input cell_id should be of type int"
    
    # Get directory name in ddddxxx format:
    dirname = format_dir_name(cell_id)
    file_ptr = TRAVEL_TIMES_BASE_DIR + dirname + "//" + TRAVEL_TIMES_FILES_PREFFIX + str(cell_id) + ".txt"
    print(f"loading file: {file_ptr}")
    travel_times = pd.read_csv(file_ptr, delimiter=";", usecols=['from_id', 'to_id', 'pt_r_t', 'car_r_t'])
    return travel_times

def style_function(feature):
    return {
        "color": "transparent",
        "fillColor": "transparent"
    }

def merge_tt_ykr(ykr_grid, tt): 
    # Merge 'from_id' geometries
    travel_times = pd.merge(tt, ykr_grid[['YKR_ID', 'geometry']], left_on='from_id', right_on='YKR_ID')
    travel_times.drop(columns=['YKR_ID', 'to_id'], inplace=True)

    tt_gdf = gpd.GeoDataFrame(travel_times, crs=ykr_grid.crs)
    tt_gdf = tt_gdf.rename(columns={'from_id': 'id'})
    return tt_gdf

def get_pt_car_diff(tt):
    tt['car_pt_diff'] = tt['car_r_t'] - tt['pt_r_t']
    return tt

# Change target cell id here! 
target_grid_cell_id = 5936715

# Load YKR Grid    
grid = load_ykr_grid()

# Load travel times to target grid & merge with YKR Grid
tt = load_traveltimes_to_grid_cell(target_grid_cell_id)    
tt = get_pt_car_diff(tt)
tt_ykr = merge_tt_ykr(grid, tt)

# Plot
mymap = folium.Map(
    location=(60.2, 24.8),
    zoom_start=12,
    control_scale=True
)

grid_layer = folium.Choropleth(
    geo_data = tt_ykr,
    data = tt_ykr,
    columns = ("id","car_pt_diff"),
    key_on="feature.properties.id",
    
    bins=9,
    fill_color="YlOrRd",
    line_weight=0,
    legend_name="Diff Car-PT travel time",

    highlight=True
)
grid_layer.add_to(mymap)


tooltip = folium.features.GeoJsonTooltip(
    fields=("id",),
    aliases=("Grid ID:",)
)

tooltip_layer = folium.features.GeoJson(
    tt_ykr,
    style_function=style_function,
    tooltip=tooltip
)
tooltip_layer.add_to(mymap)


save_and_open_map(mymap)
