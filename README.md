# NASA_Meteo_Data_Tool
Download Meteorological Data from NASA POWER API (https://power.larc.nasa.gov/)

The NASA POWER database is a global database of daily weather data
specifically designed for agrometeorological applications. The spatial
resolution of the database is 0.5x0.5 degrees (as of 2018). It is
derived from weather station observations in combination with satellite
data for parameters like radiation.
The meteorological data is updated with a delay of about 3 months which makes
the database unsuitable for real-time monitoring, nevertheless the
POWER database is useful for many other studies.
Finally, note that any latitude/longitude within a 0.5 x 0.5 degrees grid box
will yield the same weather data, e.g. there is no difference between
latitude - longitude 5.3 - 52.1 and latitude - longitude 5.1 - 52.4.
For more information on the NASA POWER database see the documentation
at: https://power.larc.nasa.gov/

#### Input parameters
```
latitude - Latitude (float)
longitude - Longitude (float)
start_date - Starting date (datetime.date)
end_date - Ending date (datetime.date)
to_PCSE - If true the tool will write the results in a format compatible to PCSE. In other case it will write as in the dataframe
to_file - Save to file if true (bool) (Optional, default = False)
filename - Name of the new file (string) (Optional, default = meteorological_data.xls)
```
#### The NASAPowerMeteorologicalData attributes
```
data - All the downloaded data in pandas dataframe (pandas dataframe)
description - A brief description of the downloaded data
elevation - Elevation in meters
latitude - Latitude
longitude - Longitude
angstormA - Angstrom A value
angstormB - Angstrom B value
power_variables - A list with the variables to download (from NASA)
```