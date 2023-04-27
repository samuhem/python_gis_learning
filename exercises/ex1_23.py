from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry import Polygon
from shapely.geometry.base import BaseGeometry
import pandas as pd


def get_origin_destination_lines(data_df):
    # Extrat origin-destination lines from input dataframe
    
    assert isinstance(data_df, pd.DataFrame), "Error: data should be instance of DataFrame"

    assert list(data.columns) == ["from_x", "from_y", "to_x", "to_y"], "Error: `data` does not (or not only) contain the four columns it should"

    origin_points = data.apply(lambda row: Point(row['from_x'], row['from_y']), axis=1).tolist()
    destination_points = data.apply(lambda row: Point(row['to_x'], row['to_y']), axis=1).tolist()

    # Check that you created a correct amount of points:
    assert len(origin_points) == len(data), "Number of origin points must be the same as number of rows in the original file"
    assert len(destination_points) == len(data), "Number of destination points must be the same as number of rows in the original file"
    
    od_lines = [LineString([origin_points[i], destination_points[i]]) for i in range(len(data))]

    # od_lines = []
    # for i in range(len(data)):
    #    od_line = Point(origin_points[i], destination_points[i])
    #    od_lines.append(od_line)
    
    return od_lines


def calculate_total_distance(lines):
    # Calculate total distance of input lines
    # lines should be a list of LineStrings
    
    total_dist = 0
    for l in lines:
        total_dist = total_dist + l.length
    
    return total_dist

data = pd.read_csv("travel_times_2015_helsinki.txt", delimiter=";")
data = data[['from_x', 'from_y', 'to_x', 'to_y']]
od_lines = get_origin_destination_lines(data)
total_dist = calculate_total_distance(od_lines)