import pandas as pd
import requests
import time
import numpy as np


def get_coord(city):
    print('Get city: ' + city)

    url = 'https://api.openrouteservice.org/geocoding?query={}&lang=en&limit=1&api_key={}' \
        .format(city + ', ' + 'Netherlands', api_key)
    dt = requests.get(url).json()
    print(dt)
    try:
        c = dt['features'][0]['geometry']['coordinates']
        # returns longitude and latitude
        return [c[1], c[0]]
    except:
        time.sleep(5)
        return get_coord(city)


api_key = '58d904a497c67e00015b45fc052fb17685174d9ca10e5dce47ccdfca'
table = pd.read_excel('List_of_large_incidents_in_NL.XLSX', usecols=['Location', 'X', 'Y'])

lat_lon = []
for location in table['Location']:

    location_query = get_coord(location)
    row = [location, location_query[0], location_query[1]]
    lat_lon.append(row)
lat_lon = pd.DataFrame(lat_lon, columns=['Location', 'latitude', 'longitude'])
writer = pd.ExcelWriter('large_incidents_lat_lon.xlsx')
lat_lon.to_excel(writer)
writer.save()



