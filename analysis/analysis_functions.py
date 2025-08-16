
import os
import math
import time
import datetime as dt
import numpy as np
import pandas as pd
import geopandas as gpd

def calculate_heat_index(temperature, relative_humidity, unit='c'):
    """
    Calculates the heat index using the Steadman formula (adapted for Celsius).

    Args:
        temperature_celsius (float): Temperature in Celsius.
        relative_humidity (float): Relative humidity as a percentage (0-100).
        unit (string): c (default) or f.

    Returns:
        float: The calculated heat index in Celsius or Fahrenheit.
    """
    if unit.lower() == 'c':
    # Convert Celsius to Fahrenheit for the Steadman formula
        temperature_fahrenheit = (temperature * 9/5) + 32
    else:
        temperature_fahrenheit = temperature
    # Steadman formula coefficients
    c1 = -42.379
    c2 = 2.04901523
    c3 = 10.14333127
    c4 = -0.22475541
    c5 = -6.83783E-03
    c6 = -5.481717E-02
    c7 = 1.22874E-03
    c8 = 8.5282E-04
    c9 = -1.99E-06

    # Calculate heat index in Fahrenheit
    heat_index_fahrenheit = (
        c1 + (c2 * temperature_fahrenheit) + (c3 * relative_humidity) +
        (c4 * temperature_fahrenheit * relative_humidity) +
        (c5 * temperature_fahrenheit**2) +
        (c6 * relative_humidity**2) +
        (c7 * temperature_fahrenheit**2 * relative_humidity) +
        (c8 * temperature_fahrenheit * relative_humidity**2) +
        (c9 * temperature_fahrenheit**2 * relative_humidity**2)
    )
    # ROthfusz regresssion is not appropriate when condtions of 
    if heat_index_fahrenheit < 80:
        heat_index_fahrenheit = 0.5 * (temperature_fahrenheit + 61.0 + ((temperature_fahrenheit-68.0)*1.2) + (relative_humidity*0.094))

    heat_index_celsius = (heat_index_fahrenheit - 32) * 5/9
    
    if unit.lower() == 'c':
    # Convert heat index back to Celsius
        return heat_index_celsius
    else:
        return heat_index_fahrenheit
    
def create_df(csv_file):
    df = pd.read_csv(csv_file)
    df = df.drop(df.index[0:6])   # The first few lines typically read funny, I will drop. First 30 seconds.
    df['datetime'] = pd.to_datetime(df['System_Timestamp_UTC'])
    df['datetime'] = df['datetime'].dt.tz_convert('America/New_York')

    # Convert 'System_Timestamp_UTC' to datetime objects
    df['System_Timestamp_UTC'] = pd.to_datetime(df['System_Timestamp_UTC'], errors='coerce')

    # Convert 'Temperature_C' and 'Humidity_RH' to numeric, coercing errors to NaN
    df['Temperature_C'] = pd.to_numeric(df['Temperature_C'], errors='coerce')
    df['Humidity_RH'] = pd.to_numeric(df['Humidity_RH'], errors='coerce')

    # Drop rows with NaN values in critical columns for plotting, as they would break the plot
    df.dropna(subset=['System_Timestamp_UTC', 'Temperature_C', 'Humidity_RH'], inplace=True)

    # I will create a geopandas dataframe as well. No need to do both.
    gdf = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.Longitude, df.Latitude))

    return df, gdf


### Testing ###
temps = [90, 85, 79, 65]
rhs = [30, 50, 70, 80]
for temp in temps:
    for rh in rhs:
        hi = calculate_heat_index(temp, rh, 'F')
        print(f'Temp: {temp} RH: {rh} = HI: {hi}')