# NASAMeteoDataTool
![nasa](https://user-images.githubusercontent.com/18232521/75673566-eb882880-5c8b-11ea-9a65-995f94b876bf.png)

Download Meteorological Data from NASA POWER restful API (https://power.larc.nasa.gov/)

The NASA POWER database is a global database of daily meteorological data
designed for agrometeorological applications and more. The spatial
resolution of the database is 0.25x0.25 degrees. Data are retrieced from in-situ observations in combination with satellite
data. The meteorological data is updated with a delay of about 3 months.
For more information on the NASA POWER database see the documentation
at: https://power.larc.nasa.gov/

### Input parameters


| Name             | Description                                                                                                                                 |
|------------------|---------------------------------------------------------------------------------------------------------------------------------------------|
| ```latitude```   | Latitude (```float```)                                                                                                                      |
| ```longitude```  | Longitude (```float```)                                                                                                                     |
| ```start_date``` | Start date (```datetime.date```)                                                                                                            |
| ```end_date```   | End date (```datetime.date```)                                                                                                              |
| ```to_PCSE```    | If true (```bool```) the tool will write the results in a format compatible to PCSE. In other case data will be written as in the dataframe.|
| ```to_file```    | Save to file if true (```bool - Optional, default = False```)                                                                               |
| ```filename```   | Name of the new file (```string - Optional, default = meteorological_data.xls```)                                                           |

### The NASAPowerMeteorologicalData class attributes

| Name                  | Description                                                                    |
|-----------------------|--------------------------------------------------------------------------------|
| ```data```            | All the downloaded data in pandas dataframe (```pandas.dataframe```)           |
| ```description```     | A brief description of the downloaded data                                     |
| ```elevation```       | Elevation in meters (m)                                                        |
| ```latitude```        | Latitude                                                                       |
| ```longitude```       | Longitude                                                                      |
| ```angstormA```       | Angstrom A value                                                               |
| ```angstormB```       | Angstrom B value                                                               |
| ```angstormB```       | Angstrom B value                                                               |
| ```power_variables``` | A list with the variables to download (from NASA)                              |

### Installation

```bash
git clone https://github.com/alekfal/NASAMeteoDataTool.git
cd NASAMeteoDataTool/
pip install .
```

### Examples

Download Meteorological data

```python
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
```

#### Results

1. Option to_PCSE = False (meteorological_data.xls):

![meteo](https://user-images.githubusercontent.com/18232521/94548147-f70af480-0258-11eb-885d-0fab180c700b.png)


2. Option to_PCSE = True (PCSE_meteorological_data.xls):

![PCSE](https://user-images.githubusercontent.com/18232521/94549025-400f7880-025a-11eb-923f-535d27dcc4f4.png)
