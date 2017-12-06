from app import db
import folium
import utm
import pandas as pd
import numpy as np
from .classes.Water_level_importer import WaterLevelImporter
from .classes.Weather_data_importer import WeatherDataImporter
from .classes.Data_merger import DataMerger
from .tablemodels import Data

      
def parse_location(x, coord='lat'):
    latM,lonM = x.strip('[').strip(']').split(',')
    lat,lon = utm.to_latlon(float(latM),float(lonM),31,'U')
    if coord == 'lat':
        return lat
    if coord == 'lon':
        return lon
    raise Exception('coord should be either lat on long')

def color_producer(waterLevel):
    if waterLevel < 100:
        return 'grey'
    if 100 <= waterLevel < 1000:
        return 'green'
    return 'blue'
   
def Create_map():
    data = pd.read_sql('data', con=db.engine,)
    data.to_csv("app/someData.csv")
    #data = pd.read_csv("app/All_weather_and_water_data.csv")
    waterlevel = data[np.isfinite(data['water_level'])]
    waterlevel_lat = list(waterlevel['latitude'])
    waterlevel_lon = list(waterlevel['longitude'])
    waterlevel_val = list(waterlevel['water_level'])
    
    humidity = data[np.isfinite(data['humidity'])]
    humidity_lat = list(humidity['latitude'])
    humidity_lon = list(humidity['longitude'])
    humidity_val = list(humidity['humidity'])
    
    tide = data[np.isfinite(data['tide']) ]
    tide_lat = list(tide['latitude'])
    tide_lon = list(tide['longitude'])
    tide_val = list(tide['tide'])
    
    
        #lat = list(map(lambda x: parse_location(x,coord='lat'),coor))
        #lon = list(map(lambda x: parse_location(x,coord='lon'),coor))
    
    fwl = folium.FeatureGroup(name="Waterlevel")
    fhm = folium.FeatureGroup(name="Humidity")
    fti = folium.FeatureGroup(name="Tide")
    
    for lt, ln, el in zip(waterlevel_lat, waterlevel_lon, waterlevel_val):
        fwl.add_child(folium.Circle(location=[lt, ln], radius = 100, popup="Waterlevel: " + str(el)+" cm",fill=True,
                                          color='blue',fill_color='blue', fill_opacity = 0.5))

    for lt, ln, el in zip(humidity_lat, humidity_lon, humidity_val):
        fhm.add_child(folium.Circle(location=[lt, ln], radius = 100, popup="Humidity: " +str(el)+" %",fill=True,
                                          color='green',fill_color='green', fill_opacity = 0.5))   
                                                                          
    for lt, ln, el in zip(tide_lat, tide_lon, tide_val):
        fti.add_child(folium.Circle(location=[lt, ln], radius = 100, popup="Tide_heigth:" + str(el)+" cm",fill=True,
                                          color='red',fill_color='red', fill_opacity = 0.5))   

    #fgv = folium.FeatureGroup(name="Waterlevel")

    #for lt, ln, el in zip(lat, lon, value):
    #    fgv.add_child(folium.Circle(location=[lt, ln], radius = 100, popup=str(el)+" cm",fill=True,
    #                                      color=color_producer(el),fill_color=color_producer(el), fill_opacity = 0.5))

    My_mapBW = folium.Map(location=[52.00, 5.60],
       zoom_start=8,
       tiles = 'http://{s}.tile.osm.org/{z}/{x}/{y}.png',
       attr='Mapbox Data Attribution')
        
    #folium.RegularPolygonMarker(location=[51.9925,  5.1364], radius = 10, popup=str(el)+" m",
    #                                      color='red',fill_color = 'red', number_of_sides=20).add_to(My_mapBW)  
    My_mapBW.add_child(folium.LatLngPopup())
    My_mapBW.add_child(fwl)
    My_mapBW.add_child(fhm)
    My_mapBW.add_child(fti)
    My_mapBW.add_child(folium.TileLayer('Mapbox Bright'))     
    My_mapBW.add_child(folium.LayerControl())
    My_mapBW.save("app/templates/map.html")  
    return map
    
def update_all_data(): 
    weather_importer = WeatherDataImporter()
    weather_importer.get_data()
    weather_importer.extract_actual_data_to_pd()
    #print(weather_importer.actual_data)
    
    water_level_importer = WaterLevelImporter()
    water_level_importer.get_all_water_data()
    water_level_importer.extract_all_to_pd()
    #print(water_level_importer.actual_data)
    
    data_merged = DataMerger(weather_importer,water_level_importer)
    data_merged.convert_water_coordinates_to_lat_lon()
    dm = data_merged.organize_map_measurements(clust_radius=0.00001)
    #print(data_merged)
    #print(dm)
    
    dm.to_sql('data', con=db.engine, if_exists='append')
    #DataTable.DataTable()
    
    return None
    
