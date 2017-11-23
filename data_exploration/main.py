from .get_weather_data import WeatherDataImporter, WaterLevelImporter

if __name__ == '__main__':

    importer = WeatherDataImporter()
    importer.get_data()
    importer.extract_actual_data_to_pd()
    print(importer.actual_data)