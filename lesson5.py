# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 11:35:52 2023

@author: S.Hemminki
"""

import pathlib
import geopandas as gpd
import numpy as np
import ssl
import contextily
import folium
import webbrowser


# fix "URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed (_ssl.c:997)>"
ssl._create_default_https_context = ssl._create_stdlib_context

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

# folium GeoJson layers expect a styling function,
# that receives each of the map’s feature and returns
# an individual style. It can, however, also return a
# static style:
def style_function(feature):
    return {
        "color": "transparent",
        "fillColor": "transparent"
    }


accessibility_grid = gpd.read_file(TRAVEL_TIMES_TO_RAILWAY_STATION_GDF_FILE)
accessibility_grid["pt_r_t"] = accessibility_grid["pt_r_t"].replace(-1, np.nan)

WFS_BASE_URL = (
    "https://kartta.hel.fi/ws/geoserver/avoindata/wfs"
    "?service=wfs"
    "&version=2.0.0"
    "&request=GetFeature"
    "&srsName=EPSG:3879"
    "&typeName={layer:s}"
)

metro = (
    gpd.read_file(
        WFS_BASE_URL.format(layer="avoindata:Seutukartta_liikenne_metro_rata")
    )
    .set_crs("EPSG:3879")
)
roads = (
    gpd.read_file(
        WFS_BASE_URL.format(layer="avoindata:Seutukartta_liikenne_paatiet")
    )
    .set_crs("EPSG:3879")
)

roads = roads.to_crs(accessibility_grid.crs)
metro = metro.to_crs(accessibility_grid.crs)

assert accessibility_grid.crs == metro.crs == roads.crs, "Input data sets’ CRS differs"

# Static maps

# Doc for gdp parameters
# https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.plot.html

# Colorbar options
# https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.colorbar.html

# Legend options
# https://matplotlib.org/stable/api/legend_api.html#matplotlib.legend.Legend

# Map tiles from online map providers are typically in Web Mercator projection (EPSG:3857. 
# It is generally advisable to transform all other layers to EPSG:3857, too.

accessibility_grid = accessibility_grid.to_crs("EPSG:3857")
metro = metro.to_crs("EPSG:3857")
roads = roads.to_crs("EPSG:3857")

ax = accessibility_grid[accessibility_grid.pt_r_t <= 15].plot(
    figsize=(12, 8),

    column="pt_r_t",
    scheme="quantiles",
    k=7,
    cmap="Spectral",
    linewidth=0,
    alpha=0.8,

    legend=True,
    legend_kwds={"title": "Travel time (min)"}
)

# By default, contextily uses the Stamen Terrain as a base map, but there are many other online maps to choose from. 
# Any of the other contextily.providers (see link above) can be passed as a source to add_basemap(). 
# For instance, use OpenStreetMap in its default Mapnik style:

# Stamen: https://maps.stamen.com/#watercolor/12/37.7706/-122.3782
contextily.add_basemap(
    ax,
    source=contextily.providers.OpenStreetMap.Mapnik,
    attribution=(
        "Travel time data (c) Digital Geography Lab, "
        "map data (c) OpenStreetMap contributors"
    )
)

# Interactive maps

# Folium docs: https://python-visualization.github.io/folium/
# Examples: https://nbviewer.org/github/python-visualization/folium/tree/main/examples/
# Quickstart tutorial: https://python-visualization.github.io/folium/quickstart.html#Getting-Started

interactive_map = folium.Map(
    location=(60.2, 24.8),
    zoom_start=10,
    control_scale=True
)

# Add a single marker
kumpula = folium.Marker(
    location=(60.204, 24.962),
    tooltip="Kumpula Campus",
    icon=folium.Icon(color="green", icon="ok-sign")
)
kumpula.add_to(interactive_map)

# Add addresses layer
addresses = gpd.read_file(DATA_DIRECTORY / "addresses.gpkg")
addresses_layer = folium.features.GeoJson(
    addresses,
    name="Public transport stops"
)
addresses_layer.add_to(interactive_map)

# Add polygon layer
population_grid = (
    gpd.read_file(
        "https://kartta.hsy.fi/geoserver/wfs"
        "?service=wfs"
        "&version=2.0.0"
        "&request=GetFeature"
        "&typeName=asuminen_ja_maankaytto:Vaestotietoruudukko_2020"
        "&srsName=EPSG:4326"
        "&bbox=24.6,60.1,25.2,60.4,EPSG:4326"
    )
    .set_crs("EPSG:4326")
)
population_grid = population_grid[["index", "asukkaita", "geometry"]]
population_grid = population_grid.rename(columns={
    "asukkaita": "population"
})

# "We will use the folium.Choropleth to display the population grid. 
# Choropleth maps are more than simply polygon geometries, 
# which could be displayed as a folium.features.GeoJson layer, 
# just like we used for the address points, above. 
# Rather, the class takes care of categorising data, adding a legend, 
# and a few more small tasks to quickly create beautiful thematic maps."
population_grid["id"] = population_grid.index.astype(str)

interactive_map = folium.Map(
    location=(60.17, 24.94),
    zoom_start=12
)

population_grid_layer = folium.Choropleth(
    geo_data=population_grid,
    data=population_grid,
    columns=("id", "population"),
    key_on="feature.id",

    bins=9,
    fill_color="YlOrRd",
    line_weight=0,
    legend_name="Population, 2020",

    highlight=True
)
population_grid_layer.add_to(interactive_map)

# More complex tooltips can be created using the
# `folium.features.GeoJsonTooltip` class. Below, we use
# its most basic features: `fields` specifies which columns
# should be displayed, `aliases` how they should be labelled.
tooltip = folium.features.GeoJsonTooltip(
    fields=("population",),
    aliases=("Population:",)
)


tooltip_layer = folium.features.GeoJson(
    population_grid,
    style_function=style_function,
    tooltip=tooltip
)
tooltip_layer.add_to(interactive_map)


# Spyder doesn't show folium.Map; open in webbrowser instead
interactive_map.save("interactive_map.html")
webbrowser.open_new_tab("interactive_map.html")

# Some other interactive maps:
# Geoviews https://geoviews.org/
# Mapbox GL for Jupyter https://github.com/mapbox/mapboxgl-jupyter
# Bokeh https://docs.bokeh.org/en/latest/docs/gallery.html
# Plotly Express https://plotly.com/python/maps/




