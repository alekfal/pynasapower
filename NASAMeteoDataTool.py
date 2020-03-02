"""
A module for downloading meteorological date from NASA Power Program.
This script is based on the relative script from the PCSE library (https://pcse.readthedocs.io/en/stable/)

Name: Falagas Alekos
Location: RSLab, SRSE-NTUA, 2019
e-mail: alek.falagas@gmail.com
Version: 0.0.1
"""

import os
import datetime as dt
import numpy as np
import pandas as pd
import requests
from requests import exceptions

from helping_functions import check_angstromAB, ea_from_tdew

# Define some lambdas to take care of unit conversions.
MJ_to_KJ = lambda x: x * 1000.
tdew_to_kpa = lambda x: ea_from_tdew(x)
to_date = lambda d: d.date()

class NASAPowerMeteorologicalData():
    """
    The NASA POWER database is a global database of daily weather data
    specifically designed for agrometeorological applications. The spatial
    resolution of the database is 0.25 x 0.25 degrees. It is
    derived from weather station observations in combination with satellite
    data for parameters like radiation.
    The weather data is updated with a delay of about 3 months which makes
    the database unsuitable for real-time monitoring, nevertheless the
    POWER database is useful for many other studies.
    Finally, note that any latitude/longitude within a 0.25 x 0.25 degrees grid box
    will yield the same weather data, e.g. there is no difference between
    latitude - longitude 5.3 - 52.1 and latitude - longitude 5.1 - 52.4.
    For more information on the NASA POWER database see the documentation
    at: https://power.larc.nasa.gov/

    The NASAPowerMeteorologicalData module retrieves daily meteorological data from the
    NASA POWER API.
    Inputs:
        * latitude - Latitude (float)
        * longitude - Longitude (float)
        * start_date - Starting date (datetime.date)
        * end_date - Ending date (datetime.date)
        * to_PCSE - If true the tool will write the results in a format compatible to PCSE. In other case it will write as in the dataframe
        * to_file - Save to file if true (bool) (Optional, default = False)
        * filename - Name of the new file (string) (Optional, default = meteorological_data.xls)
    Outputs:
        * data - All sthe downloaded data in pandas dataframe (pandas dataframe)
    """

    # Variable names in POWER data
    power_variables = ["ALLSKY_TOA_SW_DWN", "ALLSKY_SFC_SW_DWN", "T2M", "T2M_MIN",
                       "T2M_MAX", "T2MDEW", "WS2M", "PRECTOT"]
    # other constants
    HTTP_OK = 200
    angstA = 0.29
    angstB = 0.49

    def __init__(self, latitude, longitude, start_date, end_date, to_PCSE = False, to_file = False, filename = 'meteorological_data.xls'):

        # Checking coordinates
        if latitude < -90 or latitude > 90:
            raise ValueError("Latitude should be between -90 and 90 degrees.")
        if longitude < -180 or longitude > 180:
            raise ValueError("Longitude should be between -180 and 180 degrees.")

        self.latitude = latitude
        self.longitude = longitude
        self.to_file = to_file
        self.filename = filename
        self.start_date = start_date
        self.end_date = end_date
        self.to_PCSE = to_PCSE

        print ("Retrieving meteorological data from NASA Power for (lat, lon) : ({}, {}).".format(self.latitude, self.longitude))
        self.data = self._get_and_process_NASAPower(self.latitude, self.longitude, self.start_date, self.end_date, self.to_PCSE, self.to_file, self.filename)

    def _get_and_process_NASAPower(self, latitude, longitude, start_date, end_date, to_PCSE, to_file, filename):
        """
        Handles the retrieval and processing of the NASA Power data.
        Inputs:
            * latitude - Latitude (float)
            * longitude - Longitude (float)
            * start_date - Starting date (datetime.date)
            * end_date - Ending date (datetime.date)
            * to_PCSE - If true the tool will write the results in a format compatible to PCSE. In other case it will write as in the dataframe
            * to_file - Save to file if true (bool) (Optional, default = False)
            * filename - Name of the new file (string) (Optional, default = meteorological_data.xls)
        Outputs:
            * df_final - All the downloaded data in pandas dataframe (pandas dataframe)
        """

        # Sending request to server
        powerdata = self._query_NASAPower_server(latitude, longitude, start_date, end_date)
        if not powerdata:
            raise RuntimeError("Failure retrieving POWER data from server. This can be a connection problem with the NASA POWER server, retry again later.")

        # Store the informational header then parse variables
        self.description = [powerdata["header"]["title"]]
        self.elevation = float(powerdata["features"][0]["geometry"]["coordinates"][2])
        df_power = self._process_POWER_records(powerdata)

        # Determine Angstrom A, B parameters
        (self.angstA, self.angstB) = self._estimate_AngstAB(df_power)

        # Convert power records to file
        df_final = self._POWER_to_file(df_power, to_PCSE, to_file, filename)

        return (df_final)

    def _estimate_AngstAB(self, df_power):
        """
        Determine Angstrom A/B parameters from Top-of-Atmosphere (ALLSKY_TOA_SW_DWN) and
        top-of-Canopy (ALLSKY_SFC_SW_DWN) radiation values.
        The Angstrom A, B parameters are determined by dividing swv_dwn by toa_dwn
        and taking the 0.05 percentile for Angstrom A and the 0.98 percentile for
        Angstrom A+B: toa_dwn*(A+B) approaches the upper envelope while
        toa_dwn*A approaches the lower envelope of the records of swv_dwn
        values.

        Inputs:
            * df_power - dataframe with POWER data (pandas dataframe)
        Outputs:
            * angstrom_a, angstrom_b or self.angstA, self.angstB -  Angstrom A/B values (float)
        """

        print ("Starting estimation of Angstrom A/B values from NASA POWER data...")

        # Check if sufficient data is available to make a reasonable estimate
        # As a rule of thumb at least 200 days must be available
        if len(df_power) < 200:
            print ("Less then 200 days of data available. Reverting to default Angstrom A/B coefficients ({}, {})".format(self.angstA, self.angstB))
            return (self.angstA, self.angstB)

        # Calculate relative radiation (swv_dwn/toa_dwn) and percentiles
        relative_radiation = df_power.ALLSKY_SFC_SW_DWN / df_power.ALLSKY_TOA_SW_DWN
        ix = relative_radiation.notnull()
        angstrom_a = float(np.percentile(relative_radiation[ix].values, 5))
        angstrom_ab = float(np.percentile(relative_radiation[ix].values, 98))
        angstrom_b = angstrom_ab - angstrom_a

        # Checking the validity of the values
        try:
            check_angstromAB(angstrom_a, angstrom_b)
        # In other case replace them with the default values
        except:
            print ("Angstrom A/B coefficients ({}, {}) are outside of the valid range. Reverting to default values.".format(self.angstA, self.angstB))

            return (self.angstA, self.angstB)

        print ("Angstrom A/B values estimated: ({}, {}).".format(angstrom_a, angstrom_b))

        return (angstrom_a, angstrom_b)

    def _query_NASAPower_server(self, latitude, longitude, start_date, end_date):
        """
        Query the NASA Power server for data on given latitude-longitude and dates.
        Currently works only with daily data.
        Inputs:
            * latitude - Latitude (float)
            * longitude - Longitude (float)
            * start_date - Starting date (datetime.date)
            * end_date - Ending date (datetime.date)
        Outputs:
            * The response of the server in JSON format
        """

        # Build URL for retrieving data
        server = "https://power.larc.nasa.gov/cgi-bin/v1/DataAccess.py"
        payload = {"request": "execute",
            "identifier": "SinglePoint",
            "parameters": ",".join(self.power_variables),
            "lat": latitude,
            "lon": longitude,
            "startDate": start_date.strftime("%Y%m%d"),
            "endDate": end_date.strftime("%Y%m%d"),
            "userCommunity": "AG",
            "tempAverage": 'DAILY',
            "outputList": "JSON",
            "user": "anonymous"
            }

        print ("Starting retrieval from NASA Power...")
        request = requests.get(server, params = payload)

        # Check if server didn't respond to HTTP code = 200
        if request.status_code != self.HTTP_OK:
            raise exceptions.HTTPError("Failed retrieving POWER data, server returned HTTP code: {} on following URL {}.".format(request.status_code, request.url))
        # In other case is successful
        print ("Successfully retrieved data from NASA Power!")

        return (request.json())

    def _process_POWER_records(self, powerdata):
        """
        Process the meteorological records returned by NASA POWER.
        Inputs:
            * powerdata - JSON with the meteorological data.
        Outputs:
            * df_power - Dataframe with the meteorological data.
        """
        print ("Starting parsing of POWER records from URL retrieval...")

        fill_value = float(powerdata["header"]["fillValue"])

        df_power = {}
        for varname in self.power_variables:
            s = pd.Series(powerdata["features"][0]["properties"]["parameter"][varname])
            s[s == fill_value] = np.NaN
            df_power[varname] = s
        df_power = pd.DataFrame(df_power)
        df_power["DAY"] = pd.to_datetime(df_power.index, format="%Y%m%d")
        # find all rows with one or more missing values (NaN)
        ix = df_power.isnull().any(axis=1)
        # Get all rows without missing values
        df_power = df_power[~ix]

        return (df_power)

    def _write_multiple_dataframes(self, df_list, sheet, header, filename):
        """
        Saving results to excel file.
        Inputs:
            * df_list - List with the dataframes to write. (list)
            * sheet - Name of the sheet. (string)
            * header - If True writes a header (bool)
            * filename - Name of the file. (pathlike-string)
        Outputs:
            * An excel file with the data.
        """
        writer = pd.ExcelWriter(filename, engine = 'openpyxl', date_format = 'm/d/yyyy')
        row = 0
        for dataframe in df_list:
            dataframe.to_excel(writer,sheet_name = sheet,startrow = row, startcol = 0, header = header, index = False)   
            row = row + len(dataframe.index)
        
        writer.save()

    def _POWER_to_file(self, df_power, to_PCSE, to_file, filename):
        """
        A function for writing the results. Works in 2 modes:
        1. If to_PCSE is True writes the results in a format that PCSE can read.
        2. In other case simply writes the data with a header.
        Inputs:
            * df_power - Dataframe with the meteorological data (dataframe)
            * to_PCSE -  If to_PCSE is True writes the results in a format that PCSE can read. (bool)
            * to_file - If True writes the results to an excel file. (bool)
            * filename - Name of the file. (pathlike-string)
        Outputs:
            * An excel file and the final dataframe.
        """

        # If to_PCSE is True the output excel format is different
        if self.to_file == True and self.to_PCSE == True:
            # Convert POWER data to a dataframe.
            df_final = pd.DataFrame({
                "DAY": df_power.DAY.apply(to_date),
                "IRRAD": df_power.ALLSKY_SFC_SW_DWN.apply(MJ_to_KJ),
                "TMIN": df_power.T2M_MIN,
                "TMAX": df_power.T2M_MAX,
                "VAP": df_power.T2MDEW.apply(tdew_to_kpa),
                "WIND": df_power.WS2M,
                "RAIN": df_power.PRECTOT
                })
            df_final['SNOWDEPTH'] = -9999

            header = 'Site Characteristics\nCountry\nStation\nDescription\nSource\nContact\nMissing values\t-9999\nLongitude\tLatitude\tElevation\tAngstromA\tAngstromB\tHasSunshine\n{}\t{}\t{}\t{}\t{}\t0\nObserved data\nDAY\tIRRAD\tTMIN\tTMAX\tVAP\tWIND\tRAIN\tSNOWDEPTH\ndate\tkJ/m2/day or hours\tCelsius\tCelsius\tkPa\tm/sec\tmm\tcm'.format(self.longitude, self.latitude, self.elevation, self.angstA, self.angstB)
            df_header = pd.DataFrame([x.split('\t') for x in header.split('\n')])
            # Convert string values of line 8 and 6 to floats
            df_header.iloc[8] = df_header.iloc[8].astype(float)
            df_header.iloc[6, 1] = float(df_header.iloc[6, 1])
            # list of dataframes
            dfs = [df_header, df_final]

            # run function
            self._write_multiple_dataframes(dfs, 'Data', False, filename)
        
        elif self.to_file == True and self.to_PCSE == False:

            df_final = pd.DataFrame({
                "DAY": df_power.DAY.apply(to_date),
                "IRRAD": df_power.ALLSKY_SFC_SW_DWN.apply(MJ_to_KJ),
                "T2M": df_power.T2M,
                "VAP": df_power.T2MDEW.apply(tdew_to_kpa),
                "WIND": df_power.WS2M,
                "RAIN": df_power.PRECTOT})
            
            dfs = [df_final,]
            self._write_multiple_dataframes(dfs, 'Data', True, filename)

        return (df_final)