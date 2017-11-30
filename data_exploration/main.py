from classes.Water_level_importer import WaterLevelImporter
from classes.Weather_data_importer import WeatherDataImporter
from classes.Data_merger import DataMerger

weather_importer = WeatherDataImporter()
weather_importer.get_data()
weather_importer.extract_actual_data_to_pd()
#print(weather_importer.actual_data)

water_level_importer = WaterLevelImporter()
water_level_importer.get_all_water_data()
water_level_importer.extract_all_to_pd()
#print(water_level_importer.actual_data)

data_merged = DataMerger(weather_importer,water_level_importer)
dm = data_merged.organize_map_measurements()
#print(data_merged)
#print(dm)
dm.to_csv("data\All_weather_and_water_data.csv")