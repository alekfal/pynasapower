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

from .helping_functions import helpingFunctions

# Define some lambdas to take care of unit conversions.
MJ_to_KJ = lambda x: x * 1000.
tdew_to_kpa = lambda x: helpingFunctions.ea_from_tdew(x)
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
    """

    # Variable names in POWER data
    power_variables = ["ALLSKY_TOA_SW_DWN", "ALLSKY_SFC_SW_DWN", "T2M", "T2M_MIN",
                       "T2M_MAX", "T2MDEW", "WS2M", "PRECTOT"]
    # other constants
    HTTP_OK = 200
    angstA = 0.29
    angstB = 0.49

    def __init__(self, latitude, longitude, start_date, end_date, to_PCSE = False, to_file = False, filename = 'meteorological_data.xls'):
        """The NASAPowerMeteorologicalData module retrieves daily meteorological data from the NASA POWER API.

        Args:
            latitude (float): Latitude.
            longitude (float): Longitude.
            start_date (datetime.date): Starting date.
            end_date (datetime.date): Ending date.
            to_PCSE (bool, optional): If true the tool will write the results in a format compatible to PCSE. In other case it will write as in the dataframe. Defaults to False.
            to_file (bool, optional): Save to file if true. Defaults to False.
            filename (str, optional): Name of the new file. Defaults to 'meteorological_data.xls'.

        Raises:
            ValueError: Raises when latitude is not between -90 and 90 degrees.
            ValueError: Raises when longitude is not between -180 and 180 degrees.
        """
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
        """Handles the retrieval and processing of the NASA Power data.
            
        Args:
            latitude (float): Latitude.
            longitude (float): Longitude.
            start_date (datetime.date): Starting date.
            end_date (datetime.date): Ending date.
            to_PCSE (bool, optional): If true the tool will write the results in a format compatible to PCSE. In other case it will write as in the dataframe. Defaults to False.
            to_file (bool, optional): Save to file if true. Defaults to False.
            filename (str, optional): Name of the new file. Defaults to 'meteorological_data.xls'.

        Raises:
            RuntimeError: When fails to connect with the servers

        Returns:
            DataFrame: The downloaded data
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
        """Determine Angstrom A/B parameters from Top-of-Atmosphere (ALLSKY_TOA_SW_DWN) and
        top-of-Canopy (ALLSKY_SFC_SW_DWN) radiation values.
        The Angstrom A, B parameters are determined by dividing swv_dwn by toa_dwn
        and taking the 0.05 percentile for Angstrom A and the 0.98 percentile for
        Angstrom A+B: toa_dwn*(A+B) approaches the upper envelope while
        toa_dwn*A approaches the lower envelope of the records of swv_dwn
        values.

        Args:
            df_power (DataFrame): Dataframe with POWER data.

        Returns:
            tuple: Angstrom A/B values.
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
            helpingFunctions.check_angstromAB(angstrom_a, angstrom_b)
        # In other case replace them with the default values
        except:
            print ("Angstrom A/B coefficients ({}, {}) are outside of the valid range. Reverting to default values.".format(self.angstA, self.angstB))

            return (self.angstA, self.angstB)

        print ("Angstrom A/B values estimated: ({}, {}).".format(angstrom_a, angstrom_b))

        return (angstrom_a, angstrom_b)

    def _query_NASAPower_server(self, latitude, longitude, start_date, end_date):
        """Query the NASA Power server for data on given latitude-longitude and dates.
        Currently works only with daily data.

        Args:
            latitude (float): Latitude.
            longitude (float): Longitude.
            start_date (datetime.date): Starting date.
            end_date (datetime.date): Ending date.

        Raises:
            exceptions.HTTPError: Raises when fails to retrieve POWER data.

        Returns:
            dict: The response of the server in JSON format
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
        """Process the meteorological records returned by NASA POWER.

        Args:
            powerdata (dict): JSON with the meteorological data.

        Returns:
            DataFrame: Dataframe with the meteorological data.
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
        """Saving results to excel file.

        Args:
            df_list (list): List with the dataframes to write.
            sheet (str): Name of the sheet.
            header (bool): If True writes a header.
            filename (str, path-like): Name of the file.
        """
        writer = pd.ExcelWriter(filename, engine = 'openpyxl', date_format = 'm/d/yyyy')  # pylint: disable=abstract-class-instantiated
        row = 0
        for dataframe in df_list:
            dataframe.to_excel(writer,sheet_name = sheet,startrow = row, startcol = 0, header = header, index = False)   
            row = row + len(dataframe.index)
        
        writer.save()

    def _POWER_to_file(self, df_power, to_PCSE, to_file, filename):
        """A function for writing the results. Works in 2 modes:
        1. If to_PCSE is True writes the results in a format that PCSE can read.
        2. In other case simply writes the data with a header.

        Args:
            df_power (DataFrame): Dataframe with the meteorological data
            to_PCSE (bool): If to_PCSE is True writes the results in a format that PCSE can read.
            to_file (bool): If True writes the results to an excel file.
            filename (str, path-like): Name of the file.
        Returns:
            DataFrame: The final dataframe.
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