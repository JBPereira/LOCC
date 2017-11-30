from classes.Data_importer import DataImporter
import pandas as pd
#import numpy as np
#import requests
import datetime
#import os
#from functools import reduce
#import operator
from multiprocessing import Pool, cpu_count
from classes.custom_importer_exceptions import NoDataDownloadedException, DataNotUpdatedException
#import utm
#from math import radians, cos, sin, asin, sqrt
#from scipy.cluster.hierarchy import fclusterdata

class WaterLevelImporter(DataImporter):
    """
    Importer of Netherlands Water Data
    """
    def __init__(self):
        super().__init__()
        self.request_url = 'https://waterinfo.rws.nl/api/point/latestmeasurements?parameterid='
        self.request_param_list = {'water_level': 'waterhoogte-t-o-v-nap', 'waves_height': 'golfhoogte',
                                   'water_level_belgium_border': 'waterhoogte-t-o-v-taw',
                                   'tide': 'astronomische-getij', 'water_flow': 'stroming',
                                   'water_drainage': 'waterafvoer'}
        self.data_columns = {'coordinates': ['geometry', 'coordinates'], 'datetime': ['properties', 'measurements',0, 'dateTime'],
                             'value': ['properties', 'measurements', 0, 'latestValue']}
        self.update_time = 10
        self.utm_zone_code = [31, 'U']

    def get_data(self, data_to_get):
        """
        Check if the data was updated since last query. If so, get the data
        :param data_to_get: Which data to get from the Water info website
        """
        request_url = self.request_url + self.request_param_list[data_to_get]
        data, exception = self.query_data(request_url)
        if data:
            return data
        else:
            raise DataNotUpdatedException(exception)

    def get_all_water_data(self):
        cpu_number = cpu_count()
        if cpu_number > 100:  # query the different measurements in parallel
            p = Pool(cpu_number)
            try:
                data_list = p.map(self.get_data, self.request_param_list.keys())
            except DataNotUpdatedException:
                p.terminate()
                return
        else:
            data_list = []
            for measurement in self.request_param_list.keys():
                try:
                    data_list.append(self.get_data(measurement))
                except DataNotUpdatedException:
                    return

        self.last_update = datetime.datetime.now()
        data = dict(zip(self.request_param_list.keys(), data_list))
        self.latest_data = data

    def extract_actual_data_to_pd(self, data_to_extract):
        if self.latest_data:
            raw_data = self.latest_data[data_to_extract]['features']
            actual_data = pd.DataFrame(columns=self.data_columns.keys())
            for point in raw_data:
                row = {}
                for column, access in self.data_columns.items():
                    row[column] = self.get_from_dict(point, access)
                actual_data = actual_data.append(row, ignore_index=True)
            actual_data.rename(columns={'value': data_to_extract}, inplace=True)
            if self.actual_data:
                if data_to_extract in self.actual_data:
                    self.actual_data[data_to_extract].append(actual_data, ignore_index=True)
                else:
                    self.actual_data[data_to_extract] = actual_data
            else:
                self.actual_data = {data_to_extract: actual_data}
        else:
            raise NoDataDownloadedException()
            
    def extract_all_to_pd(self):
        for measurement in self.request_param_list.keys():
            self.extract_actual_data_to_pd(measurement)