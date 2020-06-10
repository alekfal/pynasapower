import datetime as dt
from pyNASAPower import NASAPowerMeteorologicalData

# Latitude, Longitude for Athens, Greece
latitude = 37.983810
longitude = 23.727539

# Dates for downloading meteorological data in format (y, m, d)
start_date = dt.date(2017, 1, 1)
end_date = dt.date(2017, 12, 31)

# Download data
meteo = NASAPowerMeteorologicalData(latitude, longitude, start_date, end_date, to_PCSE = False, to_file = True, filename = 'meteorological_data.xls')

# Or PCSE format
meteo = NASAPowerMeteorologicalData(latitude, longitude, start_date, end_date, to_PCSE = True, to_file = True, filename = 'PCSE_meteorological_data.xls')
