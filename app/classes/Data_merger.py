import pandas as pd
import numpy as np
#import requests
#import datetime
#import os
#from functools import reduce
#import operator
#from multiprocessing import Pool, cpu_count
#from custom_importer_exceptions import NoDataDownloadedException, DataNotUpdatedException
import utm
from math import radians, cos, sin, asin, sqrt
from scipy.cluster.hierarchy import fclusterdata
from .Water_level_importer import WaterLevelImporter
from .Weather_data_importer import WeatherDataImporter


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
            try:
                self.water_importer.actual_data[measurement]['coordinates'] = \
                    data['coordinates'].apply(lambda x: utm.to_latlon(*x, *utm_code))
            except ValueError:
                raise Warning('Coordinates were already converted to [lat, lon]')

    def compute_minimum_point_distance(self, clust_radius):
        coords_list = []
        point_list = []
        measurements = []
        for importer in self.importers:
            if isinstance(importer, WaterLevelImporter):
                for measurement in importer.actual_data.values():
                    coords = measurement['coordinates'].values
                    coords_list.extend(coords)
                    point_list.append(measurement)
                    measurements.extend(measurement.columns)
            elif isinstance(importer, WeatherDataImporter):
                lat = importer.actual_data['latitude'].apply(pd.to_numeric, args=('coerce',)).values
                lon = importer.actual_data['longitude'].apply(pd.to_numeric, args=('coerce',)).values
                coords_list.extend(zip(lat, lon))
                point_list.append(importer.actual_data)
                measurements.extend(importer.actual_data.columns)
        coords_list = np.array(coords_list)
        dist_matrix = np.zeros((coords_list.shape[0], coords_list.shape[0]))
        for index_i, point_i in enumerate(coords_list):
            for index_j, point_j in enumerate(coords_list):
                dist_matrix[index_i, index_j] = self.haversine(point_i, point_j)
                #         dist_matrix = squareform(pdist(point_list))
        np.fill_diagonal(dist_matrix, np.inf)
        min_point_idx = np.argmin(dist_matrix, axis=1)
        min_point_distances = dist_matrix[np.arange(dist_matrix.shape[0]), min_point_idx]
        min_point_distances_mean = np.mean(min_point_distances)
        min_point_distances_std = np.std(min_point_distances)
        clust = fclusterdata(coords_list, t=clust_radius, criterion='distance', metric=self.haversine)
        return clust, point_list, measurements

    @staticmethod
    def haversine(point1, point2):
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees) # convert decimal degrees to radians
        """
        lat1, lon1 = point1
        lat2, lon2 = point2
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        # Radius of earth in kilometers is 6371
        km = 6371 * c
        return km

    def organize_map_measurements(self, clust_radius=0.05):
        point_list = {}
        clust, point_list, measurements = self.compute_minimum_point_distance(clust_radius)
        point_index = 0
        print(measurements)
        measurements = pd.Series(measurements).unique()
        df = pd.DataFrame(columns=measurements)
        for data in point_list:
            for index, row in data.iterrows():
                labels = list(row.axes[0])
                point_clust = clust[point_index]
                df.loc[point_clust, labels] = row.values
                point_index = point_index + 1  # use loc to update column/ values
                if 'coordinates' in labels:
                    df.loc[point_clust, ['latitude', 'longitude']] = row['coordinates']
        df['datetime'] = df[['datetime', 'date_time']].fillna('').sum(axis=1)
        df.drop('coordinates', axis=1, inplace=True)
        df.drop('date_time', axis=1, inplace=True)
        return df

    @staticmethod
    def hash_point(point):
        """
        Converts a point coordinate to a hash string. Precision +-2Km
        :param point: point in format (latitude, longitude)
        :return: hash_string to map all nearby points to the same location
        """
        lat, lon = point
        if isinstance(lat, float):
            lat = np.round(point[0] * 100) / 100
        if isinstance(lon, float):
            lon = np.round(point[1] * 100) / 100
        str_lat = str(lat)
        str_lon = str(lon)
        int_lat, dec_lat = str_lat.split('.')
        int_lon, dec_lon = str_lon.split('.')
        if len(int_lat) < 2:
            int_lat = '0' + int_lat
        elif len(int_lon) < 2:
            int_lon = '0' + int_lon
        hash_string = int_lat + int_lon + dec_lat[0] + dec_lon[0]
        print('current hash_string: {}'.format(hash_string))
        if len(dec_lat) > 1:
            hash_dec_lat = str(int(np.floor(int(dec_lat[1]) / 4.0)))
            hash_string = hash_string + hash_dec_lat
        if len(dec_lon) > 1:
            hash_dec_lon = str(int(np.floor(int(dec_lon[1]) / 4.0)))
            hash_string = hash_string + hash_dec_lon
        print(hash_string)
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

    def insert_into_point_list(self, coords, point, point_list):
        point_hash = self.hash_point(coords)
        if point_hash not in point_list:
            point_list[point_hash] = point
        else:
            point_list[point_hash].append(point)
        return point_list

    def merge_weather_and_water(self):
        weather_data = self.weather_importer.actual_data
