from app import db
import folium
import utm
import pandas as pd
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
    data = pd.read_csv("app/All_weather_and_water_data.csv")
    lat = list(data["latitude"])
    lon = list(data["longitude"])
    value = list(data["water_level"])
    #lat = list(map(lambda x: parse_location(x,coord='lat'),coor))
    #lon = list(map(lambda x: parse_location(x,coord='lon'),coor))

    fgv = folium.FeatureGroup(name="Waterlevel")

    for lt, ln, el in zip(lat, lon, value):
        fgv.add_child(folium.Circle(location=[lt, ln], radius = 100, popup=str(el)+" cm",fill=True,
                                          color=color_producer(el),fill_color=color_producer(el), fill_opacity = 0.5))

    My_mapBW = folium.Map(location=[52.00, 5.60],
       zoom_start=8,
       tiles = 'http://{s}.tile.osm.org/{z}/{x}/{y}.png',
       attr='Mapbox Data Attribution')
        
    #folium.RegularPolygonMarker(location=[51.9925,  5.1364], radius = 10, popup=str(el)+" m",
    #                                      color='red',fill_color = 'red', number_of_sides=20).add_to(My_mapBW)  
    My_mapBW.add_child(folium.LatLngPopup())
    My_mapBW.add_child(fgv)
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
    
