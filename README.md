# pynasapower
![nasa](https://user-images.githubusercontent.com/18232521/75673566-eb882880-5c8b-11ea-9a65-995f94b876bf.png)

[![Build Status](https://github.com/alekfal/pynasapower/actions/workflows/python-package.yml/badge.svg?branch=main)](https://github.com/alekfal/pynasapower/actions)
[![Documentation Status](https://readthedocs.org/projects/pynasapower/badge/?version=latest)](https://pynasapower.readthedocs.io/en/latest/?badge=latest)
[![Code coverage](https://codecov.io/gh/alekfal/pynasapower/branch/main/graph/badge.svg)](https://codecov.io/gh/alekfal/pynasapower)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/pynasapower.svg?style=flat-square)](https://pypi.org/project/pynasapower/)
[![Overall downloads](https://pepy.tech/badge/pynasapower)](https://pepy.tech/project/pynasapower)
[![Last month downloads](https://pepy.tech/badge/pynasapower/month)](https://pepy.tech/project/pynasapower)

Download meteorological data from NASA POWER restful API (https://power.larc.nasa.gov/) using pynasapower API client.

The NASA POWER database is a global database of daily meteorological data designed for agrometeorological applications and more. 
Data are retrieced from in-situ observations in combination with satellite data. The meteorological data is updated with a delay of about 3 months. For more information on the NASA POWER database see the documentation at: https://power.larc.nasa.gov/

### Installation from source

```bash
git clone https://github.com/alekfal/pynasapower.git
cd pynasapower/
pip install .
```

### Instalation from PyPI

```bash
pip install pynasapower
```

### Examples

Download meteorological data for a point in Athens, Greece and save result in `*.csv` format.

```python
from pynasapower.get_data import query_power
from pynasapower.geometry import point, bbox
import datetime

# Run for point in Athens and save the result in csv format
gpoint = point(23.727539, 37.983810, "EPSG:4326")
start = datetime.date(2022, 1, 1)
end = datetime.date(2022, 2, 1)
data = query_power(gpoint, start, end, "./data", True, "ag", [], "daily", "point", "csv")
```

Download meteorological data for a polygon in Athens, Greece and save result in `*.csv` format.

```python
# Run for small bbox in Athens and save the result in csv format
gbbox = bbox(23.727539, 26.73, 37.983810, 40.99, "EPSG:4326")
start = datetime.date(2022, 1, 1)
end = datetime.date(2022, 2, 1)
data = query_power(gpoint, start, end, "./data", True, "ag", [], "daily", "regional", "csv")
```

Read more about the software in readthedocs.