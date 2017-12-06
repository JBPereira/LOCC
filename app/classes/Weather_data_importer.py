from .Data_importer import DataImporter
import pandas as pd
#import numpy as np
#import requests
import datetime
#import os
#from functools import reduce
#import operator
#from multiprocessing import Pool, cpu_count
from .custom_importer_exceptions import NoDataDownloadedException, DataNotUpdatedException
#import utm
#from math import radians, cos, sin, asin, sqrt
#from scipy.cluster.hierarchy import fclusterdata

class WeatherDataImporter(DataImporter):
    """
    Importer of Weather Data
    """

    def __init__(self):
        super().__init__()
        self.update_time = 10
        self.request_url = 'https://api.buienradar.nl/data/public/1.1/jsonfeed'
        self.data_columns = {'date_time': 'datum', 'latitude': 'lat',
                             'longitude': 'lon', 'humidity': 'luchtvochtigheid',
                             'temperature_10cm': 'temperatuur10cm', 'temperature': 'temperatuurGC',
                             'wind_direction': 'windrichting', 'wind_direction_degrees': 'windrichtingGR',
                             'wind_speedBF': 'windsnelheidBF', 'wind_speedMS': 'windsnelheidMS',
                             'wind_blast': 'windstotenMS', 'visibility_meters': 'zichtmeters',
                             'sun_intensity': 'zonintensiteitWM2'}

    def get_data(self):
        """
        Check if the data was updated since last query. If so, get the data
        """

        data, exception = self.query_data(self.request_url)
        if data:
            self.last_update = datetime.datetime.now()
            data = data['buienradarnl']['weergegevens']
            self.latest_data = data
        else:
            raise DataNotUpdatedException(exception)

    def extract_actual_data_to_pd(self):
        if self.latest_data:
            weather_station_data = self.latest_data['actueel_weer']['weerstations']['weerstation']
            actual_data = pd.DataFrame(columns=self.data_columns.keys())
            for station in weather_station_data:
                new_entry = {}
                for column, measurement in self.data_columns.items():
                    station_measurement = station[measurement]
                    if station_measurement == '-':
                        new_entry[column] = None
                    else:                    
                        new_entry[column] = station[measurement]
                actual_data = actual_data.append(new_entry, ignore_index=True)
            if self.actual_data:
                self.actual_data.append(actual_data, ignore_index=True)
            else:
                self.actual_data = actual_data
        else:
            raise NoDataDownloadedException()
