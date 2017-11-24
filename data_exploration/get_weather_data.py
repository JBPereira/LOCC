import pandas as pd
import numpy as np
import requests
import datetime
import os
from functools import reduce
import operator
from multiprocessing import Pool, cpu_count
from . import custom_importer_exceptions
import utm
from scipy.spatial.distance import squareform, pdist
import math


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

    def read_actual_data(self, data_path):

        # Reading the file

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
            raise custom_importer_exceptions.DataNotUpdatedException(exception)

    def extract_actual_data_to_pd(self):

        if self.latest_data:
            weather_station_data = self.latest_data['actueel_weer']['weerstations']['weerstation']

            actual_data = pd.DataFrame(columns=self.data_columns.keys())

            for station in weather_station_data:
                new_entry = {}

                for column, measurement in self.data_columns.items():
                    new_entry[column] = station[measurement]

                actual_data = actual_data.append(new_entry, ignore_index=True)

            if self.actual_data:
                self.actual_data.append(actual_data, ignore_index=True)
            else:
                self.actual_data = actual_data

        else:
            raise custom_importer_exceptions.NoDataDownloadedException()


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

        self.data_columns = {'coordinates': ['geometry', 'coordinates'], 'datetime': ['properties', 'measurements',
                             0, 'dateTime'], 'value': ['properties', 'measurements', 0, 'latestValue']}

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

            raise custom_importer_exceptions.DataNotUpdatedException(exception)

    def get_all_water_data(self):

        cpu_number = cpu_count()

        if cpu_number > 1:  # query the different measurements in parallel
            p = Pool(cpu_number)
            try:
                data_list = p.map(self.get_data, self.request_param_list.keys())
            except custom_importer_exceptions.DataNotUpdatedException:
                p.terminate()
                return

        else:
            data_list = []

            for measurement in self.request_param_list.keys():

                try:

                    data_list.append(self.get_data(measurement))
                except custom_importer_exceptions.DataNotUpdatedException:
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

            if self.actual_data:
                if data_to_extract in self.actual_data:
                    self.actual_data[data_to_extract].append(actual_data, ignore_index=True)
                else:
                    self.actual_data[data_to_extract] = actual_data
            else:
                self.actual_data = {data_to_extract: actual_data}

        else:
            raise custom_importer_exceptions.NoDataDownloadedException()

    def extract_all_to_pd(self):

        for measurement in self.request_param_list.keys():
            self.extract_actual_data_to_pd(measurement)


class DataMerger:

    def __init__(self, *data_importer_instances):

        number_of_importers = len(data_importer_instances)

        self.importers = data_importer_instances

        if number_of_importers < 2:

            raise ValueError('Constructor requires at least 2 Data Importer Instances')

        for importer in data_importer_instances:

            if isinstance(importer, WaterLevelImporter):

                self.water_importer = importer

            elif isinstance(importer, WeatherDataImporter):

                self.weather_importer = importer

    def convert_water_coordinates_to_lat_lon(self):

        utm_code = self.water_importer.utm_zone_code

        for measurement, data in self.water_importer.actual_data.items():
            self.water_importer.actual_data[measurement]['coordinates'] = \
                data['coordinates'].apply(lambda x: utm.to_latlon(*x, *utm_code))

    def compute_minimum_point_distance(self):

        point_list = []

        for importer in self.importers:

            if isinstance(importer, WaterLevelImporter):

                for measurement in importer.actual_data.values():
                    coords = measurement['coordinates'].values
                    point_list.extend(coords)

            elif isinstance(importer, WeatherDataImporter):
                lat = importer.actual_data['latitude'].apply(pd.to_numeric, args=('coerce',)).values
                lon = importer.actual_data['longitude'].apply(pd.to_numeric, args=('coerce',)).values
                point_list.extend(zip(lat, lon))

        point_list = np.array(point_list)

        print(point_list)

        dist_matrix = squareform(pdist(point_list))
        np.fill_diagonal(dist_matrix, np.inf)

        min_point_idx = np.argmin(dist_matrix, axis=1)
        min_point_distances = dist_matrix[np.arange(dist_matrix.shape[0]), min_point_idx]
        min_point_distances_mean = np.mean(min_point_distances)
        min_point_distances_std = np.std(min_point_distances)

        return min_point_idx, min_point_distances, min_point_distances_mean, min_point_distances_std

    @staticmethod
    def hash_point(point):

        """
        Converts a point coordinate to a hash string. Precision +-2Km
        :param point: point in format (latitude, longitude)
        :return: hash_string to map all nearby points to the same location
        """

        rounded_lat = np.round(point[0]*100)/100

        rounded_lon = np.round(point[1] * 100) / 100

        str_lat = str(rounded_lat)
        str_lon = str(rounded_lon)

        int_lat, dec_lat = str_lat.split('.')
        int_lon, dec_lon = str_lon.split('.')

        if len(int_lat) < 2:
            int_lat = '0' + int_lat
        elif len(int_lon) < 2:
            int_lat = '0' + int_lon

        hash_string = int_lat + int_lon + dec_lat[0] + dec_lon[0]

        hash_dec_lat = np.floor(int(dec_lat[1]) / 2.0)

        hash_dec_lon = np.floor(int(dec_lon[1]) / 2.0)

        hash_string = hash_string + hash_dec_lat + hash_dec_lon

        return hash_string

    @staticmethod
    def location_from_hash_string(hash_string):

        """
        From the hash s
        :param hash_string: hash_string as generated by function @hash_point
        :return: (Latitude, Longitude)
        """

        latitude = hash_string[0:2] + '.' + hash_string[4] + hash_string[6]
        longitude = hash_string[3:5] + '.' + hash_string[5] + hash_string[7]

        return np.array([np.float(latitude), np.float(longitude)])

    def merge_weather_and_water(self):

        weather_data = self.weather_importer.actual_data
