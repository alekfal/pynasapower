import requests
from requests import exceptions
import geopandas as gpd
import pandas as pd
from io import StringIO
import xarray as xr
import datetime
import os

DEFAULT_POWER_VARIABLES = ["TOA_SW_DWN", "ALLSKY_SFC_SW_DWN", "T2M", "T2M_MIN", "T2M_MAX", "T2MDEW", "WS2M", "PRECTOTCORR"]
HTTP_OK = 200

def query_power(geometry:gpd.GeoDataFrame, start:datetime.date, end:datetime.date, to_file:bool = True, path:str = "./",
    community:str = "ag", parameters:list = [],  temporal_api:str = "hourly",
    spatial_api:str = "point", format:str = "csv"):
    """
    Query NASA Power API for climate data based on the specified geometry, temporal range, and parameters.

    Parameters:
        geometry (gpd.GeoDataFrame): GeoDataFrame containing either a Point or a Polygon geometry.
        start (datetime.date): Start date for the data retrieval in datetime.date format. Note in case of monthly or climatology temporal_api only the year is used.
        end (datetime.date): End date for the data retrieval in datetime.date format.Note in case of monthly or climatology temporal_api only the year is used.
        path (str, optional): Path to the directory where the retrieved data files will be saved. Default is './'.
        to_file (bool, optional): Whether to save the data to files or not. Default is True.
        community (str, optional): NASA Power community to query data from. Default is "ag".
        parameters (list, optional): List of parameter names to retrieve. Default is an empty list. If it is not provided variables TOA_SW_DWN, "ALLSKY_SFC_SW_DWN, T2M, T2M_MIN, T2M_MAX, T2MDEW, WS2M, PRECTOTCORR are downloaded.
        temporal_api (str, optional): Temporal resolution for the data (e.g., "hourly", "daily", "monthly", "climatology"). Default is "hourly".
        spatial_api (str, optional): Spatial resolution for the data (e.g., "point", "regional"). Default is "point".
        format (str, optional): Format for the retrieved data files (e.g., "csv", "netcdf", "json", "ascii"). Default is "csv".

    Returns:
        xr.Dataset or pd.DataFrame or dict: Retrieved data in dictionary format in case of format = 'json', pd.DataFrame in case of format = 'csv' or 'ascii' and xr.Dataset in case of format = 'netcdf'.

    Note:
        - The geometry parameter must be a GeoDataFrame containing either a Point or a Polygon geometry.
        - The start and end parameters must be in datetime.date format.
        - The temporal_api parameter must be one of: "hourly", "daily", "monthly", "climatology".
        - The spatial_api parameter must be one of: "point", "regional".
        - The format parameter must be one of: "csv", "netcdf", "json", "ascii".
    """

    available_temporal = ["hourly", "daily", "monthly", "climatology"]
    if temporal_api not in available_temporal:
        raise ValueError(f"Argument 'temporal_resolution' must be one of: {', '.join(t for t in available_temporal)}")
    
    available_communities = ["ag", "sb", "re"]
    if community not in available_communities:
        raise ValueError(f"Argument 'community' must be one of: {', '.join(c for c in available_communities)}")    
    
    available_spatial = ["point", "regional"] # No global because NASA does not support it
    if spatial_api not in available_spatial:
        raise ValueError(f"Argument 'spatial_api' must be one of: {', '.join(s for s in available_spatial)}")

    available_formats = ["netcdf", "ascii", "json", "csv"]
    if format not in available_formats:
        raise ValueError(f"Argument 'format' must be one of: {', '.join(f for f in available_formats)}")
    
    if temporal_api == "hourly" and spatial_api != "point":
        raise ValueError(f"For temporal_resolution = 'hourly' spatial_api can only be point!")
    
    if parameters == []:
        parameters = DEFAULT_POWER_VARIABLES

    if temporal_api == "hourly" and len(parameters)>15:
        raise ValueError("A maximum of 15 parameters can currently be requested in one submission.")
    
    if temporal_api == "daily" and len(parameters)>20:
        raise ValueError("A maximum of 20 parameters can currently be requested in one submission.")
    
    if temporal_api == "monthly" and len(parameters)>20:
        raise ValueError("A maximum of 20 parameters can currently be requested in one submission.")

    if temporal_api == "climatology" and len(parameters)>20:
        raise ValueError("A maximum of 20 parameters can currently be requested in one submission.") 

    # Tests until here

    if not isinstance(geometry, gpd.GeoDataFrame):
        raise TypeError("Argument 'geometry' must be a GeoDataframe.")
    
    if len(geometry) > 1:
        raise ValueError("Only one geometry must be provided.")
    
    if (geometry.geom_type.iloc[0] != "Point") and (geometry.geom_type.iloc[0] != "Polygon"):
        raise ValueError("Argument geometry must be either a Point or a Polygon")

    if (geometry.geom_type.iloc[0] != "Point") and (spatial_api == "point"):
        raise ValueError("Argument geometry must be a Point since argument spatial_api is point. Try to use pynasapower.geometry.point() to create a valid point.")
    
    if (geometry.geom_type.iloc[0] != "Polygon") and (spatial_api == "regional"):
        raise ValueError("Argument geometry must be a Polygon since argument spatial_api is regional.Try to use pynasapower.geometry.bbox() to create a valid polygon.")
    
    if geometry.geom_type.iloc[0] == "Point":
        latitude = geometry.geometry.y.iloc[0]
        longitude = geometry.geometry.x.iloc[0]
        coordinates = {
            "latitude": latitude,
            "longitude": longitude,
            }

    if geometry.geom_type.iloc[0] == "Polygon":
        latitude_min = geometry.bounds.miny.iloc[0]
        latitude_max = geometry.bounds.maxy.iloc[0]
        longitude_min = geometry.bounds.minx.iloc[0]
        longitude_max = geometry.bounds.maxx.iloc[0]
        
        if latitude_max - latitude_min < 2:
            raise ValueError("Please provide at least a 2 degree range in latitude; otherwise use the point endpoint.")
        
        if longitude_max - longitude_min < 2:
            raise ValueError("Please provide at least a 2 degree range in longitude; otherwise use the point endpoint.")

        coordinates = {
            "latitude-min": latitude_min,
            "latitude-max": latitude_max,
            "longitude-min": longitude_min,
            "longitude-max": longitude_max,
            }
    

    if not isinstance(start, datetime.date):
        raise TypeError("Argument 'start' must be datetime.date object.")    
    
    if not isinstance(end, datetime.date):
        raise TypeError("Argument 'end' must be datetime.date object.")
    
    if start > end:
        raise ValueError("Argument 'start' cannot be later than 'end'!")
    
    if temporal_api in ["monthly", "climatology"]:
        start_date = start.strftime("%Y")
        end_date = end.strftime("%Y")
        if temporal_api == "climatology":
            if int(end_date) - int(start_date) < 2:
                raise ValueError("Please provide at least a two year range to compute a climatology.") 
    else:
        start_date = start.strftime("%Y%m%d")
        end_date = end.strftime("%Y%m%d")
    
    server = f"https://power.larc.nasa.gov/api/temporal/{temporal_api}/{spatial_api}?"

    params = {
            "parameters": ",".join(parameters),
            "community": community,
            "start": start_date,
            "end": end_date,
            "format": format
            }
    
    params.update(coordinates)
    
    print ("Starting retrieval from NASA Power...")
    request = requests.get(server, params = params)
    # Check if server didn't respond to HTTP code = 200
    if request.status_code != HTTP_OK:
        raise exceptions.HTTPError(f"Failed retrieving POWER data, server returned HTTP code: {request.status_code} on following URL {request.url}.")
    # In other case is successful
    print ("Successfully retrieved data from NASA Power!")
    
    name = request.headers['content-disposition'].split("=")[1]
    
    if format == "netcdf":
        data = xr.open_dataset(request.content)
        data.to_netcdf(os.path.join(path, name))
    elif format == "csv" or format == "ascii":
        string = request.content.decode("utf-8")
        # Split the data into header and actual data
        header, string = string.split("-END HEADER-")
        data_lines = string.strip().split('\n')

        # Create a StringIO object for the data and load it into a DataFrame
        data_io = StringIO("\n".join(data_lines))
        data = pd.read_csv(data_io)
        
        if to_file:
            # Write header to txt
            txt_name = name.split(".")[0] + "_variables.txt"
            with open(os.path.join(path, txt_name), "w") as dst:
                dst.write(header)
            if format == "ascii":
                data.to_csv(os.path.join(path, name), sep='\t', index=False)
            else:
                data.to_csv(os.path.join(path, name), index=False)
    else:
        string = request.content.decode("utf-8")
        with open(os.path.join(path, name), "w") as outfile:
            outfile.write(string)
        
        data = request.json()
    
    return data