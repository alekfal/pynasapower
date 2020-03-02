# NASA_Meteo_Data_Tool
![nasa](https://user-images.githubusercontent.com/18232521/75673566-eb882880-5c8b-11ea-9a65-995f94b876bf.png)

Download Meteorological Data from NASA POWER API (https://power.larc.nasa.gov/)

The NASA POWER database is a global database of daily weather data
specifically designed for agrometeorological applications. The spatial
resolution of the database is 0.25x0.25 degrees. It is
derived from weather station observations in combination with satellite
data for parameters like radiation.
The meteorological data is updated with a delay of about 3 months which makes
the database unsuitable for real-time monitoring, nevertheless the
POWER database is useful for many other studies.
Finally, note that any latitude/longitude within a 0.25 x 0.25 degrees grid box
will yield the same weather data, e.g. there is no difference between
latitude - longitude 5.3 - 52.1 and latitude - longitude 5.1 - 52.4.
For more information on the NASA POWER database see the documentation
at: https://power.larc.nasa.gov/

#### Input parameters

1. latitude - Latitude (float)
2. longitude - Longitude (float)
3. start_date - Starting date (datetime.date)
4. end_date - Ending date (datetime.date)

Optionals:

5. to_PCSE - If true the tool will write the results in a format compatible to PCSE. In other case it will write as in the dataframe
6. to_file - Save to file if true (bool) (Optional, default = False)
7. filename - Name of the new file (string) (Optional, default = meteorological_data.xls)

#### The NASAPowerMeteorologicalData attributes

data - All the downloaded data in pandas dataframe (pandas dataframe)
description - A brief description of the downloaded data
elevation - Elevation in meters
latitude - Latitude
longitude - Longitude
angstormA - Angstrom A value
angstormB - Angstrom B value
power_variables - A list with the variables to download (from NASA)
<<<<<<< HEAD

#### Examples

Download Meteorological data

```
import datetime as dt
from NASAMeteoDataTool import NASAPowerMeteorologicalData

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
```


=======
```
>>>>>>> 12d455df843fdc85419a3b2b06187a408d95b187
