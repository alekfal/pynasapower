# pynasapower
![nasa](https://user-images.githubusercontent.com/18232521/75673566-eb882880-5c8b-11ea-9a65-995f94b876bf.png)

[![Build Status](https://github.com/alekfal/pynasapower/actions/workflows/python_package.yml/badge.svg?branch=main)](https://github.com/alekfal/pynasapower/actions/workflows/python_package.yml)
[![Documentation Status](https://readthedocs.org/projects/pynasapower/badge/?version=latest)](https://pynasapower.readthedocs.io/en/latest/?badge=latest)
[![Code coverage](https://codecov.io/gh/alekfal/pynasapower/branch/main/graph/badge.svg)](https://codecov.io/gh/alekfal/pynasapower)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/pynasapower.svg?style=flat-square)](https://pypi.org/project/pynasapower/)
[![Overall downloads](https://pepy.tech/badge/pynasapower)](https://pepy.tech/project/pynasapower)
[![Last month downloads](https://pepy.tech/badge/pynasapower/month)](https://pepy.tech/project/pynasapower)

Download meteorological data from NASA POWER restful API (https://power.larc.nasa.gov/) using pynasapower API client.

The NASA POWER database is a global database of daily meteorological data designed for agrometeorological applications and more. 
Data are retrieced from in-situ observations in combination with satellite data. For more information on the NASA POWER database see the documentation at: https://power.larc.nasa.gov/.

### Installation from source

```bash
git clone https://github.com/alekfal/pynasapower.git
cd pynasapower/
pip install .
```

### Installation from PyPI

```bash
pip install pynasapower
```

### NASA POWER API client arguments

- `geometry`: Single point or polygon geometry as `geopandas.GeoDataFrame`. User can use methods pynasapower.geometry.point() or
pynasapower.geometry.bbox() to create an input geometry for this client.
- `start`: Start date as `datetime.date` format. In the examples the value is `datetime.date(2022, 1, 1)`. 
- end: End date as `datetime.date` format. In the examples the value
is `datetime.date(2022, 2, 1)`.
- `path`: Local path to store the downloaded data. In the examples `"./"` is used.
- `to_file`: Boolean argument to save data locally. By default is `True`.
- `community`: The default POWER `community` is agroclimatology (`"ag"`). Other available communities are sustainable buildings (`"sb"`) and renewable energy (`"re"`). Find more about the POWER communities [here](https://power.larc.nasa.gov/docs/methodology/communities/).
- `parameters`: The default parameters for downloading (`["TOA_SW_DWN", "ALLSKY_SFC_SW_DWN", "T2M", "T2M_MIN", "T2M_MAX", "T2MDEW", "WS2M", "PRECTOTCORR"]`) are selected for downloading if an empty list (`[]`) is provided by the user. Find more for the POWER parameters in [here](https://power.larc.nasa.gov/#resources).
- temporal_api: Temporal resolution of the data. The default value is `"daily"`. Other selections are  `"hourly"`, `"monthly"`, `"climatology"`. Read more about the temporal resolution of the data [here](https://power.larc.nasa.gov/docs/services/api/temporal/).
- `spatial_api`: Spatial resolution of the data. By default `"point"` is selected, but a user can also use `"regional"`. Note that in order to download a region a polygon geometry must be used in the `geometry` argument.
- `format`: Output format of the data. The default is `"csv"`. Other selections supported by the API client are: `"netcdf"`, `"json"` and `"ascii"`. 


### Quickstart

Download meteorological data for a point in Athens, Greece and save result in `*.csv` format.

```python
from pynasapower.get_data import query_power
from pynasapower.geometry import point, bbox
import datetime

# Run for point in Athens and save the result in csv format
gpoint = point(23.727539, 37.983810, "EPSG:4326")
start = datetime.date(2022, 1, 1)
end = datetime.date(2022, 2, 1)
data = query_power(geometry = gpoint, start = start, end = end, path = "./data", to_file = True, community = "ag", parameters = [], temporal_api = "daily", spatial_api = "point", format = "csv")
```

Download meteorological data for a polygon in Athens, Greece and save result in `*.csv` format.

```python
# Run for small bbox in Athens and save the result in csv format
gbbox = bbox(23.727539, 26.73, 37.983810, 40.99, "EPSG:4326")
start = datetime.date(2022, 1, 1)
end = datetime.date(2022, 2, 1)
data = query_power(geometry = gbbox, start = start, end = end, path = "./data", to_file = True, community = "ag", parameters = [], temporal_api = "daily", spatial_api = "point", format = "csv")
```

Read more about the software in project's [readthedocs](https://pynasapower.readthedocs.io/en/latest/).