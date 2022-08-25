import folium, json
import pandas as pd
from folium import plugins
import csv
with open('NH.geojson') as f:
    NH = json.load(f)
NH_map = folium.Map(location=[43.209568, -71.53729], tiles='Stamen Toner', zoom_start = 9)
folium.GeoJson(NH).add_to(NH_map)
with open('loco.csv', newline='') as file:
    reader = csv.DictReader(file)
    for row in reader:
        if(int(row['pm25']) < 10):
            folium.CircleMarker((row['latitude'],row['longitude']), radius = 10, weight = 2, color = 'green', fill_color='green', fill_opacity=0.5).add_child(folium.Popup("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm25'])).add_to(NH_map)
        else:
            folium.CircleMarker((row['latitude'],row['longitude']), radius = 10, weight = 2, color = 'red', fill_color='red', fill_opacity=0.5).add_child(folium.Popup(row['name'],row['pm25'])).add_to(NH_map)
    NH_map.save('nhPointMap.html')