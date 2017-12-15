# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 14:03:18 2017

@author: espoelst
"""
import datetime
import pandas as pd
import utm
import folium
from math import radians, cos, sin, asin, sqrt
import time
import re


def convert_datetime_to_same(dateori):
    datetime_object = datetime.datetime.strptime(dateori, '%Y%m%d')
    date = datetime_object.strftime('%d-%m-%Y')
    return date


def lat_lon_convert(x):
    lat,lon = utm.to_latlon(x[0],x[1],31,'U')
    return lat,lon

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

def read_weather_data():
    ##Start creating weather data
    wd_columns_to_keep = ['   FG','   TG','   SQ','   RH','   PG','   UX',' EV24','YYYYMMDD','# STN']
    WeaterData = pd.read_csv("KNMI_20171203 - Copy.csv",sep = ";")
    WeaterData.columns
    WeaterData = WeaterData[wd_columns_to_keep]
    
    STNDict = pd.read_csv('STNcoor.csv',sep= ';')
    
    stnactualdict = {k:v for k,v in zip(list(STNDict['# STN']),list(STNDict['NAME']))}
    WeaterData['Name'] = WeaterData['# STN'].map(stnactualdict)
    stnactualdict = {k:v for k,v in zip(list(STNDict['# STN']),list(STNDict['LAT(north)']))}
    WeaterData['LAT'] = WeaterData['# STN'].map(stnactualdict)
    stnactualdict = {k:v for k,v in zip(list(STNDict['# STN']),list(STNDict['LON(east)']))}
    WeaterData['LON'] = WeaterData['# STN'].map(stnactualdict)
    WeaterData = WeaterData.drop('# STN',axis = 1)
    
    WeaterData['YYYYMMDD'] = list(map(lambda x: convert_datetime_to_same(str(x)),WeaterData['YYYYMMDD']))
    WeaterData['TIME'] = "08:00:00"
    
    WeaterData.rename(columns={'   FG': 'WindSpeed', '   TG': 'Temp', '   SQ': 'Sunshine', '   RH': 'Precipitation',
                               '   PG': 'SeaLevelPressure', '   UX': 'Humidity', ' EV24': 'Evapotranspiration',
                               'YYYYMMDD': 'DATE'}, inplace=True)
    WeaterData.columns

    timeArray = WeaterData.apply(lambda x: datetime.datetime.strptime(x['DATE'],'%d-%m-%Y'),axis = 1)
    timeIndex = timeArray>=datetime.date(1953,1,1)
    WeaterData = WeaterData.loc[timeIndex,:]
    WeaterData.drop_duplicates()
    return WeaterData 
    ##end creting weather data

IncidentData = pd.read_csv("List_of_large_incidents_in_NL.csv",  sep = ";",encoding='utf-8')
IncidentData = IncidentData[IncidentData['Incident type'].str.contains("Overstroming")] 

def read_water_data():
    ##start Creating water level data set
    wl_columns_to_keep = ["MEETPUNT_IDENTIFICATIE",'WAARNEMINGDATUM','WAARNEMINGTIJD','NUMERIEKEWAARDE','X','Y']
    WLData = pd.read_csv("WL1953.csv",sep = ";")
    WL1953Data = WLData[wl_columns_to_keep]
    WLData = pd.read_csv("WL1962.csv",sep = ";")
    WL1962Data = WLData[wl_columns_to_keep]
    WLData = pd.read_csv("WL1993.csv",sep = ";")
    WL1993Data = WLData[wl_columns_to_keep]
    WLData = pd.read_csv("WL1995.csv",sep = ";")
    WL1995Data = WLData[wl_columns_to_keep]
    WLData = pd.read_csv("WL2003.csv",sep = ";",encoding='latin-1')
    WL2003Data = WLData[wl_columns_to_keep]
    WLdata = WL1953Data.append(WL1962Data).append(WL1993Data).append(WL1995Data).append(WL2003Data)
    
    WLdata['Y'] = WLdata['Y'].map(lambda x: float(x.replace(",",".")))
    WLdata['X'] = WLdata['X'].map(lambda x: float(x.replace(",",".")))
    
    aaa = WLdata[['X','Y']].apply(lat_lon_convert,axis = 1)
    WLdata['LAT'] = [item[0] for item in aaa]
    WLdata['LON'] = [item[1] for item in aaa]
    WLdata = WLdata.drop('X',axis = 1)
    WLdata = WLdata.drop('Y',axis = 1)
    
    WLdata.rename(columns={'MEETPUNT_IDENTIFICATIE': 'Name', 'WAARNEMINGDATUM': 'DATE', 'WAARNEMINGTIJD': 'TIME', 'NUMERIEKEWAARDE': 'WaterLevel'}, inplace=True)
    WLdata['Name'] = WLdata['Name'].apply(lambda x : re.sub('[(){}<>]', '', x))
    WLdata.drop_duplicates()
    WLdata.columns
    return WLdata
    ## end creating Water level dataset

def inefficient_table_creator(dataframe1,dataframe2):
    AllDataFrame = pd.DataFrame(columns = list(['WindSpeed', 'Temp', 'Sunshine', 'Precipitation', 'SeaLevelPressure', 'Humidity', 'Evapotranspiration','Distance']) + list(WLdata.columns))
    #AllDataFrame.drop(['LAT','LON','DATE','TIME'],axis=1)

    for latWat,lonWat,dateWat,timeWat in zip(dataframe1['LAT'],dataframe1['LON'],dataframe1['DATE'],dataframe1['TIME']):
        start = time.time()
        shortest_distance = None
        shortest_distance_coordinates = None
        MyPoint = (latWat,lonWat)  
        DateTimeWL = (dateWat,timeWat)
        WeatherAtDate = dataframe2[(dataframe2['DATE']== DateTimeWL[0])].drop_duplicates(['LAT','LON'])
        
        pointInstance = WeatherAtDate.loc[:,['LAT','LON']].apply(lambda x: haversine(MyPoint,(x)),axis=1)
        shortest_distance  = pointInstance.min()
        shortest_distance_coordinates = (WeatherAtDate.loc[pointInstance.argmin()]['LAT'],WeatherAtDate.loc[pointInstance.argmin()]['LON'])
        
        dfWeather = WeatherAtDate[WeatherAtDate['LAT'] == shortest_distance_coordinates[0]].iloc[0]
        dfWeather = dfWeather.drop(['LAT','LON','DATE','TIME','Name'])
        dfWater = dataframe1[(dataframe1['LAT']==MyPoint[0]) & (dataframe1['LON']==MyPoint[1])
            &(dataframe1['DATE']==DateTimeWL[0])&(dataframe1['TIME']==DateTimeWL[1])].iloc[0]
        dfWater['Distance'] = shortest_distance
        AllDataFrame = AllDataFrame.append(pd.concat([dfWeather,dfWater],ignore_index=False),ignore_index=True)
        end = time.time()
        print(end - start)
    return AllDataFrame

WLdata = read_water_data()
WeatherData = read_weather_data()
#AllDataFrame = inefficient_table_creator(WLdata ,WeatherData)

WLdata.head()
WeatherData.head()
WLdataNoDups = WLdata.drop_duplicates(['LAT','LON'])
WeatherdataNoDups =  WeatherData.drop_duplicates(['LAT','LON'])

AllDistDataFrame = pd.DataFrame()

for latWat,lonWat in zip(WLdataNoDups['LAT'],WLdataNoDups['LON']):
    start = time.time()
    shortest_distance = None
    shortest_distance_coordinates = None
    MyPoint = (latWat,lonWat)  
            
    pointInstance = pd.DataFrame(WeatherdataNoDups.loc[:,['LAT','LON']].apply(lambda x: haversine(MyPoint,(x)),axis=1))
    pointNames = pd.DataFrame(WeatherdataNoDups.loc[pointInstance.index.values]['Name'])
    pointBoth = pointInstance.join(pointNames).sort_values(0)
    pointTuple = pd.DataFrame([list(zip(pointBoth['Name'],pointBoth[0]))])
    pointTuple['WLName'] = WLdataNoDups[WLdataNoDups['LAT']==latWat]['Name'].tolist()
    AllDistDataFrame = AllDistDataFrame.append(pointTuple,ignore_index =True)

AllDistDataFrame = AllDistDataFrame.set_index('WLName')

AllDataFrame = pd.DataFrame(columns = list(['WindSpeed', 'Temp', 'Sunshine', 'Precipitation', 'SeaLevelPressure', 'Humidity', 'Evapotranspiration','Distance']) + list(WLdata.columns))    
dataframe1  = WLdata
dataframe2 =  WeatherData
start = time.time()
for row in dataframe1.iterrows():
    WeatherAtDate = dataframe2[(dataframe2['DATE']== row[1]['DATE'])].drop_duplicates(['Name'])
    for i in range(0,50):
        try:
            DistanceTuple = list(AllDistDataFrame[AllDistDataFrame.index.str.contains(row[1]['Name'],False)][i])[0]
            dfWeather = WeatherAtDate[WeatherAtDate['Name']==DistanceTuple[0]]
            if dfWeather.empty:            
                raise ValueError('Weather at data was empty.')
            dfWeather['Distance']= DistanceTuple[1]
            break
        except:
            #print('PROBLEMS!!')
            continue

    dfWeather = dfWeather.drop(['LAT','LON','DATE','TIME','Name'],axis=1)
    dfWater = row[1]
    AllDataFrame = AllDataFrame.append(pd.concat([dfWeather.iloc[0],dfWater],ignore_index=False),ignore_index=True)

end = time.time()
print(end - start)


#WLdata.shape
#WLdata1 = WLdata[WLdata['WaterLevel']<=10000].drop_duplicates()
#WLdata1.groupby('DATE').count()


#for lat,lon in zip(WLdataNoDups ['LAT'],WLdataNoDups ['LON']):
 

        
        

  
##Visualize the coordinates
WLdataNoDups = WLdata.drop_duplicates(['LAT','LON'])
WeatherdataNoDups =  WeaterData.drop_duplicates(['LAT','LON'])

fwl = folium.FeatureGroup(name="Waterlevel")
fhm = folium.FeatureGroup(name="Humidity")
for lt, ln, el in zip(WLdataNoDups['LAT'],WLdataNoDups['LON'], WLdataNoDups['WaterLevel']):
    fhm.add_child(folium.Circle(location=[lt, ln], radius = 300, popup="Waterlevel: " + str(el)+" km/h",fill=True,
                                          color='blue',fill_color='blue', fill_opacity = 0.5))

for lt, ln, el in zip(WeatherdataNoDups['LAT'], WeatherdataNoDups['LON'], WeatherdataNoDups['WindSpeed']):
    fwl.add_child(folium.Circle(location=[lt, ln], radius =300, popup="Humidity: " +str(el)+" cm",fill=True,
                                          color='red',fill_color='red', fill_opacity = 0.5))   

My_mapBW = folium.Map(location=[52.00, 5.60], zoom_start=8,tiles='OpenStreetMap')
My_mapBW.add_child(fwl)
My_mapBW.add_child(fhm)
My_mapBW.save("map.html")  