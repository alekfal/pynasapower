import pytest
import geopandas as gpd
from shapely.geometry import Point, Polygon, MultiPolygon
from contextlib import suppress as do_not_raise
import datetime
from pynasapower.get_data import query_power
from pynasapower.geometry import point, bbox
import random
import string
import pandas as pd
import xarray as xr

gpoint = point(23.727539, 37.983810, "EPSG:4326")
gbbox = bbox(23., 25., 37., 39., "EPSG:4326")
start = datetime.date(2022, 1, 1)
end = datetime.date(2022, 2, 1)


# For testing with random letters as parameters
r_params = [random.choice(string.ascii_letters) for _ in range(21)]
# ----

# For testing with wrong geometry
wrong_geom = Point([0.0, 1.0])
# ----

# For testing with multiple points geometry
# Generate random coordinates for two points
point1 = Point(random.uniform(-180, 180), random.uniform(-90, 90))
point2 = Point(random.uniform(-180, 180), random.uniform(-90, 90))
# Create a GeoDataFrame with the random points
data = {'ID': [1, 2], 'geometry': [point1, point2]}
gdf_two_points = gpd.GeoDataFrame(data, geometry='geometry')
# ----

# For testing with multipolygon
# Number of polygons in the MultiPolygon
num_polygons = random.randint(1, 5)

# Generate random polygons and create a MultiPolygon
polygons = []
for _ in range(num_polygons):
    num_points = random.randint(3, 10)
    coordinates = [(random.uniform(-180, 180), random.uniform(-90, 90)) for _ in range(num_points)]
    polygon = Polygon(coordinates)
    polygons.append(polygon)

multipolygon = MultiPolygon(polygons)

# Create a GeoDataFrame with the random MultiPolygon
multipolygon = gpd.GeoDataFrame(geometry=[multipolygon])
# ----

# For testing dates
wrong_start_date_format = "20170101"
wrong_end_date_format = "20180101"
# ----

# For testing start later than end
start_later = datetime.date(2022, 4, 1)
end_later = datetime.date(2022, 2, 1)

# For testing in regional request latitude and longitude values more than 2 degrees.
gbbox_invalid_lon = bbox(20., 20.1, 37., 39.1, "EPSG:4326")
gbbox_invalid_lat = bbox(20., 22.1, 37., 37.1, "EPSG:4326")

params = [
    (gpoint, start, end, True, "./data", "ag", [], "random", "point", "csv", pytest.raises(ValueError)),
    (gpoint, start, end, True, "./data", "random", [], "hourly", "point", "csv", pytest.raises(ValueError)),
    (gpoint, start, end, True, "./data", "ag", [], "hourly", "random", "csv", pytest.raises(ValueError)),
    (gpoint, start, end, True, "./data", "ag", [], "hourly", "point", "random", pytest.raises(ValueError)),
    (gbbox, start, end, True, "./data", "ag", [], "hourly", "regional", "csv", pytest.raises(ValueError)),
    (gpoint, start, end, True, "./data", "ag", r_params, "hourly", "point", "csv", pytest.raises(ValueError)),
    (gpoint, start, end, True, "./data", "ag", r_params, "daily", "point", "csv", pytest.raises(ValueError)),
    (gpoint, start, end, True, "./data", "ag", r_params, "monthly", "point", "csv", pytest.raises(ValueError)),
    (wrong_geom, start, end, True, "./data", "ag", [], "monthly", "point", "csv", pytest.raises(TypeError)),
    (gdf_two_points, start, end, True, "./data", "ag", [], "monthly", "point", "csv", pytest.raises(ValueError)),
    (multipolygon, start, end, True, "./data", "ag", [], "monthly", "regional", "csv", pytest.raises(ValueError)),
    (gpoint, start, end, True, "./data", "ag", [], "monthly", "regional", "csv", pytest.raises(ValueError)),
    (gbbox, start, end, True, "./data", "ag", [], "monthly", "point", "csv", pytest.raises(ValueError)),
    (gpoint, wrong_start_date_format, end, True, "./data", "ag", [], "monthly", "point", "csv", pytest.raises(TypeError)),
    (gpoint, start, wrong_end_date_format, True, "./data", "ag", [], "monthly", "point", "csv", pytest.raises(TypeError)),
    (gpoint, start_later, end_later, True, "./data", "ag", [], "monthly", "point", "csv", pytest.raises(ValueError)),
    (gpoint, start, end, True, "./data", "ag", [], "climatology", "point", "csv", pytest.raises(ValueError)),
    (gbbox_invalid_lon, start, end, True, "./data", "ag", [], "monthly", "regional", "csv", pytest.raises(ValueError)),
    (gbbox_invalid_lat, start, end, True, "./data", "ag", [], "monthly", "regional", "csv", pytest.raises(ValueError)),

    ]

@pytest.mark.parametrize("geometry, start, end, to_file, path, community, parameters, temporal_api, spatial_api, format, exception", params,)
def test_get_data_invalid(geometry, start, end, to_file, path, community, parameters, temporal_api, spatial_api, format, exception):
    with exception:  
        result = query_power(geometry, start, end, to_file, path, community, parameters, temporal_api, spatial_api, format)

# For testing climatology

start_climatology = datetime.date(2020, 1, 1)
end_climatology = datetime.date(2022, 1, 1)

params_valid_csv = [
    (gpoint, start, end, True, "./data", "ag", [], "daily", "point", "csv"),
    (gpoint, start, end, True, "./data", "ag", [], "daily", "point", "ascii"),
    ]

@pytest.mark.parametrize("geometry, start, end, to_file, path, community, parameters, temporal_api, spatial_api, format", params_valid_csv,)
def test_get_data_valid_csv(geometry, start, end, to_file, path, community, parameters, temporal_api, spatial_api, format):
    result = query_power(geometry, start, end, to_file, path, community, parameters, temporal_api, spatial_api, format)
    assert isinstance(result, pd.DataFrame)

params_valid_netcdf = [
    (gbbox, start, end, True, "./data", "ag", [], "monthly", "regional", "netcdf"),
    ]

@pytest.mark.parametrize("geometry, start, end, to_file, path, community, parameters, temporal_api, spatial_api, format", params_valid_netcdf,)
def test_get_data_valid_netcdf(geometry, start, end, to_file, path, community, parameters, temporal_api, spatial_api, format):
    result = query_power(geometry, start, end, to_file, path, community, parameters, temporal_api, spatial_api, format)
    assert isinstance(result, xr.Dataset)

params_valid_json = [
    (gbbox, start, end, True, "./data", "ag", [], "monthly", "regional", "json"),
    ]

@pytest.mark.parametrize("geometry, start, end, to_file, path, community, parameters, temporal_api, spatial_api, format", params_valid_json,)
def test_get_data_valid_json(geometry, start, end, to_file, path, community, parameters, temporal_api, spatial_api, format):
    result = query_power(geometry, start, end, to_file, path, community, parameters, temporal_api, spatial_api, format)
    assert isinstance(result, dict)