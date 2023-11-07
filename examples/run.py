from pynasapower.get_data import query_power
from pynasapower.geometry import point, bbox
import datetime

# Run for point in Athens and save the result in csv format
gpoint = point(23.727539, 37.983810, "EPSG:4326")
start = datetime.date(2022, 1, 1)
end = datetime.date(2022, 2, 1)
data = query_power(gpoint, start, end, "./data", True, "ag", [], "daily", "point", "csv")

# Run for small bbox in Athens and save the result in csv format
gbbox = bbox(23.727539, 26.73, 37.983810, 40.99, "EPSG:4326")
start = datetime.date(2022, 1, 1)
end = datetime.date(2022, 2, 1)
data = query_power(gpoint, start, end, "./data", True, "ag", [], "daily", "regional", "csv")