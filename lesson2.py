import geopandas
import pathlib

PROJECT_ROOT = pathlib.Path().resolve()
DATA_DIRECTORY = PROJECT_ROOT / "data"
TOPOGRAPHIC_DATABASE_DIRECTORY = DATA_DIRECTORY / "finland_topographic_database"


#nuts_regions = geopandas.read_file("https://gisco-services.ec.europa.eu/distribution/v2/nuts/shp/NUTS_RG_60M_2021_3035.shp.zip")
#nuts_regions.head()
# nuts_regions.to_file(DATA_DIRECTORY / "europe_nuts_regions.geojson")


population_grid = geopandas.read_file(
    "https://kartta.hsy.fi/geoserver/wfs"
    "?service=wfs"
    "&version=2.0.0"
    "&request=GetFeature"
    "&typeName=asuminen_ja_maankaytto:Vaestotietoruudukko_2020"
    "&srsName=EPSG:3879"
    "&bbox=25494767,6671328,25497720,6673701,EPSG:3879",
    crs="EPSG:3879"
)
population_grid.head()


input_filename = list(TOPOGRAPHIC_DATABASE_DIRECTORY.glob("m*p.shp"))[0] 
data = geopandas.read_file(input_filename)
data = data[["RYHMA", "LUOKKA", "geometry"]]
data = data.rename(
    columns={
        "RYHMA": "GROUP",
        "LUOKKA": "CLASS"
    }
)


data.at[0, "geometry"]
print(f"Area: {round(data.at[0, 'geometry'].area)} m².")

data["area"] = data.area
lakes = data[data.CLASS == 36200]

lakes.to_file(DATA_DIRECTORY / "finland_topographic_database" / "lakes.shp")

grouped_data = data.groupby("CLASS")

for key, group in grouped_data:
    print(f"Terrain class {key} has {len(group)} rows.")
    
# Iterate over the input data, grouped by CLASS
for key, group in data.groupby("CLASS"):
    # save the group to a new shapefile
    group.to_file(TOPOGRAPHIC_DATABASE_DIRECTORY / f"terrain_{key}.shp")