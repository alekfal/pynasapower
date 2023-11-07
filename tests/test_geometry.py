import pytest
from contextlib import suppress as do_not_raise
import geopandas as gpd
from shapely.geometry import Polygon
from pynasapower.geometry import point, bbox


point_params = [("23.727539", "37.983810", "EPSG:4326", None, pytest.raises(TypeError), 23.727539, 37.983810),
                (23.727539, "37.983810", "EPSG:4326", None, pytest.raises(TypeError), 23.727539, 37.983810),
                (23.727539, 37.983810, "EPSG:4326", "1", pytest.raises(TypeError), 23.727539, 37.983810),
                (23.727539, 37.983810, 1, None, pytest.raises(TypeError), 23.727539, 37.983810),
                (23.727539, 37.983810, "4326", None, pytest.raises(ValueError), 23.727539, 37.983810),
                (23.727539, 37.983810, "EPSG:4326", None, do_not_raise(), 23.727539, 37.983810),
                (472398.11, 4205245.48, "EPSG:2100", None, do_not_raise(), 23.68734, 37.99705),
                ]

tolerances = [.01]
@pytest.mark.parametrize("x, y, crs, z, exception, latitude, longitude", point_params,)
@pytest.mark.parametrize('tolerance', tolerances)
def test_point(x, y, crs, z, exception, latitude, longitude, tolerance):
    with exception:
        geometry = point(x, y, crs, z)
        assert isinstance(geometry, gpd.GeoDataFrame)
        assert pytest.approx(float(geometry.geometry.x.iloc[0]), tolerance) == latitude
        assert pytest.approx(float(geometry.geometry.y.iloc[0]), tolerance) == longitude

params = [
    (0.0, 1.0, 0.0, 1.0, "EPSG:4326"),  # Use a valid EPSG code
    (-180.0, 180.0, -90.0, 90.0, "EPSG:4326"),  # Use a valid EPSG code
    (0.0, 1.0, 0.0, 1.0, "EPSG:4326"),  # Use a valid EPSG code
]

@pytest.mark.parametrize("x_min, x_max, y_min, y_max, crs", params)
def test_bbox_valid_inputs(x_min, x_max, y_min, y_max, crs):
    bbox_result = bbox(x_min, x_max, y_min, y_max, crs)
    assert isinstance(bbox_result, gpd.GeoDataFrame)
    assert bbox_result.crs == "EPSG:4326"  # Check if the result has been reprojected to EPSG:4326
    
    # Use almost_equals with a tolerance for floating-point comparison
    expected_geometry = Polygon([(x_min, y_min), (x_min, y_max), (x_max, y_max), (x_max, y_min)])
    assert bbox_result.geom_equals_exact(expected_geometry, tolerance = .001).iloc[0]

params = [
    ("a", 1.0, 0.0, 1.0, "EPSG:4326"),  # Test with non-numeric x_min
    (0.0, 1.0, 0.0, "b", "EPSG:4326"),  # Test with non-numeric y_max
    (0.0, 1.0, 0.0, 1.0, 12345),  # Test with non-string crs
    (0.0, 1.0, 0.0, 1.0, "INVALID:4326"),  # Test with invalid crs format
    (2.0, 1.0, 0.0, 1.0, "EPSG:4326"),  # Test with x_min greater than x_max
    (0.0, 1.0, 2.0, 1.0, "EPSG:4326"),  # Test with y_min greater than y_max
    ]

@pytest.mark.parametrize("x_min, x_max, y_min, y_max, crs", params)
def test_bbox_invalid_inputs(x_min, x_max, y_min, y_max, crs):
    with pytest.raises((TypeError, ValueError)):
        bbox(x_min, x_max, y_min, y_max, crs)