import geopandas as gpd
from shapely.geometry import Polygon
from typing import Union

def point(x:Union[float, int], y:Union[float, int], crs:str, z:Union[float, int]=None):
    """Generate a Point GeoDataFrame to be inserted in the API client.

    Args:
        x (float): X coordinate. In case of geographical coordinates add longitude as x
        y (float): Y coordinate. In case of geographical coordinates add latitude as y
        crs (str): Reference code of coordinate system. For reference codes of the most commonly used projections, see spatialreference.org
    
    Returns:
        gpd.GeoDataFrame: Geometry as geodataframe
    """
    if (not isinstance(x, float)) and (not isinstance(x, int)):
        raise TypeError("X coordinate must be a float or int!")
    
    if (not isinstance(y, float)) and (not isinstance(y, int)):
        raise TypeError("Y coordinate must be a float")

    if z is not None:
        if (not isinstance(z, float)) and (not isinstance(z, int)):
            raise TypeError("Z coordinate must be a float or int!")
    
    if not isinstance(crs, str):
        raise TypeError("crs must be a str!")
    
    if not crs.startswith("EPSG:"):
        raise ValueError("crs must start with EPSG:... Try to find the reference code at spatialreference.org!")
    
    geometry = gpd.GeoDataFrame([], geometry=gpd.points_from_xy([x], [y], [z]), crs=crs)

    if geometry.crs != "EPSG:4326": # Force EPSG:4326 to properly interact with the API 
        geometry = geometry.to_crs("EPSG:4326")

    return geometry

def bbox(x_min:Union[float, int], x_max:Union[float, int], y_min:Union[float, int], y_max:Union[float, int], crs:str):
    """Create a bounding box polygon using minimum and maximum coordinates along with a coordinate reference system (CRS).
    This function takes minimum and maximum x and y coordinates, and a CRS code, and creates a GeoDataFrame containing a bounding box polygon.
    The function performs input validation to ensure the correctness of the input parameters.

    Parameters:
        x_min (float or int): Minimum x-coordinate of the bounding box. In case of geographical coordinates add longitude as x
        x_max (float or int): Maximum x-coordinate of the bounding box. In case of geographical coordinates add longitude as x
        y_min (float or int): Minimum y-coordinate of the bounding box. In case of geographical coordinates add latitude as y
        y_max (float or int): Maximum y-coordinate of the bounding box. In case of geographical coordinates add latitude as y
        crs (str): Coordinate Reference System (CRS) code in the format "EPSG:XXXX", where XXXX is the EPSG code representing the CRS. For reference codes of the most commonly used projections, see spatialreference.org

    Returns:
        gpd.GeoDataFrame: A GeoDataFrame containing a bounding box polygon represented as a Shapely Polygon object
    """
    if (not isinstance(x_min, float)) and (not isinstance(x_min, int)):
        raise TypeError("x_min coordinate must be a float or int!")

    if (not isinstance(x_max, float)) and (not isinstance(x_max, int)):
        raise TypeError("x_max coordinate must be a float or int!")

    if (not isinstance(y_min, float)) and (not isinstance(y_min, int)):
        raise TypeError("y_min coordinate must be a float or int!")  
    
    if (not isinstance(y_max, float)) and (not isinstance(y_max, int)):
        raise TypeError("y_max coordinate must be a float or int!")

    if x_min > x_max:
        raise ValueError("max_x value cannot be smaller than x_min!")
    
    if y_min > y_max:
        raise ValueError("max_y value cannot be smaller than y_min!")
    
    if not isinstance(crs, str):
        raise TypeError("crs must be a str!")
    
    if not crs.startswith("EPSG:"):
        raise ValueError("crs must start with EPSG:... Try to find the reference code at spatialreference.org!")
    
    geometry = Polygon([(x_min, y_min), (x_min, y_max), (x_max, y_max), (x_max, y_min)])

    bbox = gpd.GeoDataFrame(geometry=[geometry], crs = crs)
    
    if bbox.crs != "EPSG:4326": # Force EPSG:4326 to properly interact with the API 
        bbox = bbox.to_crs("EPSG:4326")
    
    return bbox