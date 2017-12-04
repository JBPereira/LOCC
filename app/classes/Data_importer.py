import pandas as pd
import numpy as np
import requests
import datetime
import os
from functools import reduce
import operator
#from multiprocessing import Pool, cpu_count
#from custom_importer_exceptions import NoDataDownloadedException, DataNotUpdatedException
#import utm
#from math import radians, cos, sin, asin, sqrt
#from scipy.cluster.hierarchy import fclusterdata


class DataImporter:
    """
    Base Class for Importers
    """
    def __init__(self):
        self.last_update = None
        self.latest_data = None
        self.actual_data = None
        self.update_time = None
        self.data_columns = None

    def read_actual_data(self, data_path):# Reading the file
        return pd.read_csv(data_path, names=self.data_columns.keys())

    def check_last_updated(self):
        current_time = datetime.datetime.now()
        if self.last_update:
            time_passed_since_last_update = current_time - self.last_update
            minutes_passed_since_last_update = time_passed_since_last_update.total_seconds() / 60
        else:
            minutes_passed_since_last_update = np.inf
        if minutes_passed_since_last_update < self.update_time:
            return False, minutes_passed_since_last_update
        else:
            return True, None

    def query_data(self, request_url):
        can_update, minutes_to_update = self.check_last_updated()
        if can_update:
            data = requests.get(request_url).json()
            return data, None
        else:
            exception = 'Data was not updated yet, wait {} minutes'.format(minutes_to_update)
            return False, exception

    @staticmethod
    def write_to_file(data, data_path):
        if os.path.exists(data_path):
            with open(data_path, 'a') as f:
                data.to_csv(f, encoding='utf-8', header=False)
        else:
            data.to_csv(data_path, encoding='utf-8', header=True)

    @staticmethod
    def get_from_dict(data_dict, map_list):
        return reduce(operator.getitem, map_list, data_dict)