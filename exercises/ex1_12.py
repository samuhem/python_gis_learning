from shapely.geometry import Point
from shapely.geometry import LineString
from shapely.geometry import Polygon
from shapely.geometry.base import BaseGeometry


def create_point_geom(x, y):
    return Point(x,y)


def create_line_geometry(points_list):
    if type(points_list) is not list:
        raise TypeError("Input should be a list")
    
    assert len(points_list) >= 2, "At minimum two points are required for a LineString"
    
    for p in points_list:
        assert isinstance(p, Point), "All list values must be of type shapely.geometry.Point"
    
    
    return LineString(points_list)


def create_polygon_geometry(coords):
    if type(coords) is not list:
        raise TypeError("Input should be a list")
        
    assert len(coords) >= 3, "At minimum three points are required for a Polygon"
        
    for point in coords:
        if not (isinstance(point, tuple) and len(point) == 2):
            raise ValueError("All list values must be coordinate tuples")
            
        if not all(isinstance(c, (int, float)) for c in point):
            raise ValueError("All tuple values must be instances of either int or float")
            
    return Polygon(coords)

def get_centroid(geom):
    assert isinstance(geom, BaseGeometry), "Input must be a shapely geometry"
    return geom.centroid


def get_area(polygon):
    assert isinstance(polygon, Polygon), "Input must be a shapely Polygon"
    return polygon.area


def get_length(geometry):
    if isinstance(geometry, LineString):
        return geometry.length
    elif isinstance(geometry, Polygon):
        return geometry.exterior.length
    else:
        raise ValueError("Input must be either a shapely.geometry.LineString or a shapely.geometry.Polygon")

    return geometry.len



point1 = create_point_geom(0.0, 1.1)
print(point1)
print(point1.geom_type)


point2 = create_point_geom(45.2, 22.34)
point3 = create_point_geom(100.22, -3.20)
line1 = create_line_geometry(list([point2, point3]))

points_list = [(1, 2), (3, 4), (5, 6)]

# Example input geometries
polygon = Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])
line = LineString([(0, 0), (1, 1), (2, 2)])

try:
    centroid = get_centroid(polygon)
    print(f"Centroid of the polygon: {centroid}")

    centroid = get_centroid(line)
    print(f"Centroid of the line: {centroid}")
    
    
    area = get_area(polygon)
    print(f"Area of the polygon: {area}")
    
    length = get_length(line)
    print(f"Length of the line: {length}")
    
except AssertionError as e:
    print(f"Error: {e}")
    
