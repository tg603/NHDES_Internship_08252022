import csv, json, datetime, urllib.request, configparser, logging, os, shutil, geopy, pandas, folium
from math import sqrt
from datetime import datetime, date, timezone
from folium import plugins
from folium.features import DivIcon
from csv import writer
from geopy.geocoders import Nominatim

global currentDate
currentDate = date.today()
Datee = currentDate.strftime("%m%d%Y")

Timez = datetime.now().timestamp()

logName = 'Log'+ str(datetime.now().strftime('Date%m%d%YTime%H%M %S')) + '.log'
fileLocation = 'E:\\ARD_PurpleAir\\Package\\' + logName
desinationLocation = 'E:\\ARD_PurpleAir\\Package\\Logs\\' + logName
logging.basicConfig(filename = logName, filemode = 'w',level=logging.INFO)
logging.info('Start timestamp for execution is: ' + datetime.now().strftime('%m/%d/%Y %H:%M:%S'))
logging.info('Starting the execution of program Pull')

def readIni():
    try:
        logging.info('Starting readIni() method')
        global jumpreldiffthreshold, units, keywords, duplicates
        defaults = {
        'jumpreldiffthreshold': '',
        'units': '',
        'keywords': '',
        'duplicates' : '',
        } 
        config = configparser.ConfigParser(defaults,allow_no_value=True)
        config.add_section('Main')
        try:
            logging.info('Trying to open .ini file to read')
            f = open ("Demo.ini", 'r')
            logging.info('File exists')
            config.read_file(f)
            f.close()
        except:
            pass
        f = open ("Demo.ini", 'w')
        logging.info('Populating .ini file now')
        config.write(f)
        items = {x[0]:x[1] for x in config.items('Main')}
        jumpreldiffthreshold     = str(items['jumpreldiffthreshold'])
        units       = str(items['units'])
        keywords    = str(items['keywords'])
        duplicates  = str(items['duplicates'])
        logging.info('Finishing readIni() method')
    except:
        logging.error('Unexpected Error')
        logging.info('Time of program exit ' + datetime.now().strftime('%m/%d/%Y %H:%M:%S'))        

def API():
    try:
        logging.info('Starting API() method')
        mapCSVCreate()
        for unit in units.split('|'):    
            try:
                out = open (unit+"API.json","w")
                logging.info("Unit is " + unit)
                url = "https://june2022.api.purpleair.com/v1/sensors/%s"\
                        "?api_key=DB310998-0207-11ED-8561-42010A800005" % (unit)
                f = urllib.request.urlopen (url)
            except:
                logging.error('Unit is: ' + unit)
                logging.info('If blank, fill in the .ini file, save, and rerun program')
                logging.info('If unit ID is not blank, problem with connection to unit; either wrong ID or unit is down')
                logging.info('Time of program exit ' + datetime.now().strftime('%m/%d/%Y %H:%M:%S'))
            buff = f.read(); f.close()
            j = json.loads(buff)
            json.dump(j, out, indent = 2)
            out.close() 
            k = open(unit+'API.json')
            collection = json.load(k)
            strdata = str(collection)
            jsonData1 = collection["sensor"]
            jsonData2 = jsonData1["stats"]
            jsonData3 = jsonData1["stats_a"]
            jsonData4 = jsonData1["stats_b"]
            k.close()
            exists = checkToC()
            logging.info('The .CSV file exists currently: ' + str(exists))
            createCSV(collection, jsonData1, jsonData2, jsonData3, jsonData4, exists)
            # WGH Addition 08082022
            os.remove(unit + 'API.json')             
        logging.info('Finishing API() method')
    except:
        logging.error('Unexpected Error')
        logging.info('Time of program exit ' + datetime.now().strftime('%m/%d/%Y %H:%M:%S'))
        
def checkToC():
    try:
        csvcurrentfile = open('DESPurple' + Datee + '.csv', 'r')
        exists = True
        logging.info('.CSV is already made for todays pulling')
        return exists
    except:
        logging.info('.CSV hasnt been made yet for todays pulling')
        exists = False
        return exists

def helpme(jsonObject, jsonObject1, jsonObject2, jsonObject3, jsonObject4, i, keyIndex, duplicateSpecify):
    spot = keyIndex.index(i)
    number = str(duplicateSpecify[spot])
    keyIndex[spot] = ''
    value = ''
    if(number == '0'):
        if(i == "time_stamp" or i == "data_time_stamp"):
            temporary = jsonObject.get(i)
            value = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S'))
            return value
        else:
            value = str(jsonObject.get(i))
            return value
    elif(number == '1'):
        if(i == "last_modified" or i == "date_created" or i == "last_seen"):
            temporary = jsonObject1.get(i)
            value = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S'))
            return value
        else:
            value = str(jsonObject1.get(i))
            return value
    elif(number == '2'):
        if(i == "time_stamp"):
            temporary = jsonObject2.get(i)
            value = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S'))
            return value
        else:
            value = str(jsonObject2.get(i))
            return value
    elif(number == '3'):
        if(i == "time_stamp"):
            temporary = jsonObject3.get(i)
            value = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S'))
            return value
        else:
            value = str(jsonObject3.get(i))
            return value
    elif(number == '4'):
        if(i == "time_stamp"):
            temporary = jsonObject4.get(i)
            value = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S'))
            return value
        else:
            value = str(jsonObject4.get(i))
            return value
    return value
'''    
def dataValidation(pm_1, pm_2, humidity):
    read_1 = True
    read_2 = True
    numberz = (((float(pm_2) - float(pm_1))/((float(pm_2) + float(pm_1) / 2))) * 100)
    if(humidity == "None"):
        pm_1 = "NULL"
        pm_2 = "NULL"
        logging.error("No humidity reading")
        return pm_1, pm_2
    else:
        if(float(pm_1) > 10):
            if(numberz <= 70.0):
                logging.info("Channel a pm passes as valid")
            else:
                logging.error("Data for pm2.5 channel a is invalid; reads higher than 5 micrograms per cubic meter!")
                pm_1 = "NULL"
                read_1 = False
        else:
            if(float(pm_2) > 10):
                if(numberz <= 70.0):
                    logging.info("Channel b pm passes as valid")
                else:
                    logging.error("Data for pm2.5 channel b is invalid; reads higher than 5 micrograms per cubic meter!")
                    pm_2 = "NULL"
                    read_2m = False
            if(pm_1 == "NULL" and pm_2 == "NULL"):
                logging.error("Both channels read higher than 5 micrograms per cubic meter!")
                return pm_1, pm_2
            elif(read_1 == True and read_2 == True):
                temporary = ((float(pm_1) + float(pm_2)) / 2)
                return pm_1, pm_2

def SaveMyFingers(jsonObject, jsonObject1, jsonObject2, jsonObject3, jsonObject4):
    arrayEverything = []
    for i in jsonObject.keys():
        if(i == "sensor"):
            continue
        else:
            arrayEverything.append(i)
    for i in jsonObject1.keys():
        if(i == "stats" or i == "stats_a" or i == "stats_b"):
            continue
        else:
            arrayEverything.append(i)
    for i in jsonObject2.keys():
        if(i == "stats" or i == "stats_a" or i == "stats_b"):
            continue
        else:
            arrayEverything.append(i)
    for i in jsonObject3.keys():
        if(i == "stats" or i == "stats_a" or i == "stats_b"):
            continue
        else:
            arrayEverything.append(i)
    for i in jsonObject4.keys():
        arrayEverything.append(i)
    return arrayEverything
    
def locationz(long, lat):
    geolocator = Nominatim(user_agent="Purple")
    location = geolocator.reverse(str(lat) + ", " + str(long))
    obj_1 = location.raw
    try:
        obj_2 = obj_1['address']
        #print(obj_2['town'])
        return (obj_2['town'])
    except:
        pass
    try:
        obj_2 = obj_1['address']
        #print(obj_2['city'])
        return (obj_2['city'])
    except:
        pass
    try:
        obj_2 = obj_1['address']
        #print(obj_2['village'])
        return (obj_2['village'])
    except:
        pass
'''
def mapCSVCreate():
    csvcurrentfile = open('NH.csv', 'w', newline = '')
    headers = ['latitude', 'longitude', 'name', 'pm2.5']
    csv_writer = writer(csvcurrentfile)
    csv_writer.writerow(headers)
    csvcurrentfile.close()
    
def mapCSV(jsonObject1, value):
    name = jsonObject1.get("name")
    lat = jsonObject1.get("latitude")
    long = jsonObject1.get("longitude")
    pm = str(value)
    heading = []
    heading.append(lat)
    heading.append(long)
    heading.append(name)
    heading.append(pm)
    csvcurrentfile = open('NH.csv', 'a', newline = '')
    csv_writer = writer(csvcurrentfile)
    csv_writer.writerow(heading)
    csvcurrentfile.close()
'''
def calculateLatLong(lat1, long1, lat2, long2):
    from math import radians, cos, sin, asin, sqrt
    lat1 = radians(lat1)
    lat2 = radians(lat2)
    long1 = radians(long1)
    long2 = radians(long2)
    dist_lat = lat2 - lat1
    dist_long = long2 - long1
    x = sin(dist_lat/2)**2 + cos(lat1) * cos(lat2) * sin(dist_long/2)**2
    y = 2 * asin(sqrt(x))
    radius = 3956 #for miles and kilometers is 6371
    total_dist = round(float(y * radius),4)
    #print(total_dist)
    return total_dist
def airportData(lat1, long1):
    #Gets real time current humidity from an airport
    import urllib.request, requests
    KAFN_lat = 42.8051342
    KAFN_long = -72.0030219
    KASH_lat = 42.7824139
    KASH_long = -71.5140944
    KMHT_lat = 42.9328056
    KMHT_long = -71.4357500
    KCON_lat = 43.2027222 
    KCON_long = -71.5022778
    KDAW_lat = 43.280838
    KDAW_long = -70.92828
    KEEN_lat = 42.8983889
    KEEN_long = -72.2707778
    KLCI_lat = 43.57278
    KLCI_long = -71.41889
    KLEB_lat = 43.6258333333
    KLEB_long = -72.3041666667
    K1P1_lat = 43.77924
    K1P1_long = -71.75369
    KHIE_lat = 44.3676139
    KHIE_long = -71.5444694
    KBML_lat = 44.57528
    KBML_long = -71.17583 
    dist = []
    dist1 = calculateLatLong(lat1, long1, KAFN_lat, KAFN_long)
    dist.append(dist1)
    dist2 = calculateLatLong(lat1, long1, KASH_lat, KASH_long)
    dist.append(dist2)    
    dist3 = calculateLatLong(lat1, long1, KMHT_lat, KMHT_long)
    dist.append(dist3)
    dist4 = calculateLatLong(lat1, long1, KCON_lat, KCON_long)
    dist.append(dist4)
    dist5 = calculateLatLong(lat1, long1, KDAW_lat, KDAW_long)
    dist.append(dist5)
    dist6 = calculateLatLong(lat1, long1, KEEN_lat, KEEN_long)
    dist.append(dist6)
    dist7 = calculateLatLong(lat1, long1, KLCI_lat, KLCI_long)
    dist.append(dist7)
    dist8 = calculateLatLong(lat1, long1, KLEB_lat, KLEB_long)
    dist.append(dist8)
    dist9 = calculateLatLong(lat1, long1, K1P1_lat, K1P1_long)
    dist.append(dist9)
    dist10 = calculateLatLong(lat1, long1, KHIE_lat, KHIE_long)
    dist.append(dist10)
    dist11 = calculateLatLong(lat1, long1, KBML_lat, KBML_long)    
    dist.append(dist11)
    minimum = dist[0]
    #print("yesss")
    for i in range(0,11):
        #print(i)
        if(minimum > dist[i]):
            minimum = dist[i]
    #print("Minimum mileage is: " + str(minimum))
    index = dist.index(minimum)
    #print("done")
    #print("work")
    
    #webUrl = requests.get('https://www.aviationweather.gov/metar/data?ids=KAFN&format=decoded&hours=0&taf=off&layout=on')
    #web_Contents = webUrl.content
    #print(web_Contents)
    #txt_writer = writer(currentfile)
    #array_web = []
    #for i in webUrl:
    #    data = str(webUrl.readline())

    #webUrl = urllib.request.urlopen('view-source:https://www.aviationweather.gov/metar/data?ids=KAFN&format=decoded&hours=0&taf=off&layout=on')
    #print("work")

    #array_web = []
    #for i in webUrl:
        #data = str(web_Contents.readline())
        #print(data)
        #if(data.__contains__("RH")):
            #print(data.find('RH'))
            #temp = (data[124] + data[125])
            #array_web.append(temp)
        #array_web.append(webUrl.readline())
        #currentfile.writelines(webUrl.readline())
    
    #KAFN Airport in Jaffrey, NH
    
    if(index == 0):
        array_web = []
        webUrl = requests.get('https://www.aviationweather.gov/metar/data?ids=KAFN&format=decoded&hours=0&taf=off&layout=on')
        web_Contents = webUrl.text
        #print(web_Contents)
        number = int(web_Contents.find('RH'))
        sec_num = number + 6
        third_num = number + 7
        temp = (str(web_Contents[sec_num]) + str(web_Contents[third_num]))
        array_web.append(temp)
        #print(array_web)
        return temp
        #
    elif(index == 1):
        array_web = []
        webUrl = requests.get('https://www.aviationweather.gov/metar/data?ids=KASH&format=decoded&hours=0&taf=off&layout=on')
        web_Contents = webUrl.text
        #print(web_Contents)
        number = int(web_Contents.find('RH'))
        sec_num = number + 6
        third_num = number + 7
        temp = (str(web_Contents[sec_num]) + str(web_Contents[third_num]))
        array_web.append(temp)
        #print("result code: " + str(webUrl.getcode()))
        #print(array_web)
        return temp
        #print(array_web)
        #currentfile.writelines(array_web)
    elif(index == 2):
        array_web = []
        webUrl = requests.get('https://www.aviationweather.gov/metar/data?ids=KMHT&format=decoded&hours=0&taf=off&layout=on')
        web_Contents = webUrl.text
        #print(web_Contents)
        number = int(web_Contents.find('RH'))
        sec_num = number + 6
        third_num = number + 7
        temp = (str(web_Contents[sec_num]) + str(web_Contents[third_num]))
        array_web.append(temp)
        #print("result code: " + str(webUrl.getcode()))
        #print(array_web)
        return temp
    elif(index == 3):
        array_web = []
        webUrl = requests.get('https://www.aviationweather.gov/metar/data?ids=KCON&format=decoded&hours=0&taf=off&layout=on')
        web_Contents = webUrl.text
        #print(web_Contents)
        number = int(web_Contents.find('RH'))
        sec_num = number + 6
        third_num = number + 7
        temp = (str(web_Contents[sec_num]) + str(web_Contents[third_num]))
        array_web.append(temp)
        #print("result code: " + str(webUrl.getcode()))
        #print(array_web)
        return temp
    elif(index == 4):
        array_web = []
        webUrl = requests.get('https://www.aviationweather.gov/metar/data?ids=KDAW&format=decoded&hours=0&taf=off&layout=on')
        web_Contents = webUrl.text
        #print(web_Contents)
        number = int(web_Contents.find('RH'))
        sec_num = number + 6
        third_num = number + 7
        temp = (str(web_Contents[sec_num]) + str(web_Contents[third_num]))
        array_web.append(temp)
        #print("result code: " + str(webUrl.getcode()))
        #print(array_web)
        return temp
    elif(index == 5):
        array_web = []
        webUrl = requests.get('https://www.aviationweather.gov/metar/data?ids=KEEN&format=decoded&hours=0&taf=off&layout=on')
        web_Contents = webUrl.text
        #print(web_Contents)
        number = int(web_Contents.find('RH'))
        sec_num = number + 6
        third_num = number + 7
        temp = (str(web_Contents[sec_num]) + str(web_Contents[third_num]))
        array_web.append(temp)
        #print("result code: " + str(webUrl.getcode()))
        #print(array_web)
        return temp
    elif(index == 6):
        array_web = []
        webUrl = requests.get('https://www.aviationweather.gov/metar/data?ids=KLCI&format=decoded&hours=0&taf=off&layout=on')
        web_Contents = webUrl.text
        #print(web_Contents)
        number = int(web_Contents.find('RH'))
        sec_num = number + 6
        third_num = number + 7
        temp = (str(web_Contents[sec_num]) + str(web_Contents[third_num]))
        array_web.append(temp)
        #print("result code: " + str(webUrl.getcode()))
        #print(array_web)
        return temp
    elif(index == 7):
        array_web = []
        webUrl = requests.get('https://www.aviationweather.gov/metar/data?ids=KLEB&format=decoded&hours=0&taf=off&layout=on')
        web_Contents = webUrl.text
        #print(web_Contents)
        number = int(web_Contents.find('RH'))
        sec_num = number + 6
        third_num = number + 7
        temp = (str(web_Contents[sec_num]) + str(web_Contents[third_num]))
        array_web.append(temp)
        #print("result code: " + str(webUrl.getcode()))
        #print(array_web)
        return temp
    elif(index == 8):
        array_web = []
        webUrl = requests.get('https://www.aviationweather.gov/metar/data?ids=K1P1&format=decoded&hours=0&taf=off&layout=on')
        web_Contents = webUrl.text
        #print(web_Contents)
        number = int(web_Contents.find('RH'))
        sec_num = number + 6
        third_num = number + 7
        temp = (str(web_Contents[sec_num]) + str(web_Contents[third_num]))
        array_web.append(temp)
        #print("result code: " + str(webUrl.getcode()))
        #print(array_web)
        return temp
    elif(index == 9):
        array_web = []
        webUrl = requests.get('https://www.aviationweather.gov/metar/data?ids=KHIE&format=decoded&hours=0&taf=off&layout=on')
        web_Contents = webUrl.text
        #print(web_Contents)
        number = int(web_Contents.find('RH'))
        sec_num = number + 6
        third_num = number + 7
        temp = (str(web_Contents[sec_num]) + str(web_Contents[third_num]))
        array_web.append(temp)
        #print("result code: " + str(webUrl.getcode()))
        #print(array_web)
        return temp
    elif(index == 10):
        array_web = []
        webUrl = requests.get('https://www.aviationweather.gov/metar/data?ids=KBML&format=decoded&hours=0&taf=off&layout=on')
        web_Contents = webUrl.text
        #print(web_Contents)
        number = int(web_Contents.find('RH'))
        sec_num = number + 6
        third_num = number + 7
        temp = (str(web_Contents[sec_num]) + str(web_Contents[third_num]))
        array_web.append(temp)
        #print("result code: " + str(webUrl.getcode()))
        #print(array_web)
        return temp
'''
def original_mapMaking():
    from folium.plugins import FloatImage
    from folium.plugins import MarkerCluster
    import json
    from shapely.geometry import shape, Point
    import PIL
    from PIL import Image
    image_file = Image.open('Legend.png')
    image_file.putalpha(210)
    image_file = image_file.save("Legend.png")
    img = 'Legend.png'
    image_file1 = Image.open('Colors.png')
    image_file1.putalpha(190)
    image_file1 = image_file1.save("Colors.png")
    img1 = 'Colors.png'
    with open('NH.geojson') as f:
        NH = json.load(f)
    with open('NHCounty.geojson') as r:
        NH1 = json.load(r)
    with open('NHCounty2.geojson') as j:
        NH2 = json.load(j)
    with open('NHCounty3.geojson') as l:
        NH3 = json.load(l)
    with open('NHCounty4.geojson') as p:
        NH4 = json.load(p)
    with open('NHCounty5.geojson') as t:
        NH5 = json.load(t)
    with open('NHCounty6.geojson') as z:
        NH6 = json.load(z)
    with open('NHCounty7.geojson') as k:
        NH7 = json.load(k)
    NH_map = folium.Map(location=[43.209568, -71.53729], zoom_start = 9)
    style1 = {'fillColor': '#e6e6fa', 'color': '#ba55d3', 'fillOpacity': 0.4}
    style2 = {'color': '#1e90ff', 'fillOpacity': 0.20}
    style3 = {'color': '#0077be', 'fillOpacity': 0.20}
    style4 = {'color': '#4682b4', 'fillOpacity': 0.20}
    style5 = {'color': '#006db0', 'fillOpacity': 0.20}
    style6 = {'color': '#0095b6', 'fillOpacity': 0.20}
    style7 = {'color': '#006994', 'fillOpacity': 0.20}
    style8 = {'color': '#0095b6', 'fillOpacity': 0.20}
    layer = folium.GeoJson(NH,style_function=lambda x:style1, name = 'State Outline').add_to(NH_map)
    layer1 = folium.GeoJson(NH1,style_function=lambda x:style2, name = 'Belknap County').add_to(NH_map)
    layer2 = folium.GeoJson(NH2,style_function=lambda x:style3, name = 'Merrimack County').add_to(NH_map)
    layer3 = folium.GeoJson(NH3,style_function=lambda x:style4, name = 'Hillsborough County').add_to(NH_map)
    layer4 = folium.GeoJson(NH4,style_function=lambda x:style5, name = 'Cheshire County').add_to(NH_map)
    layer5 = folium.GeoJson(NH5,style_function=lambda x:style6, name = 'Rockingham County').add_to(NH_map)
    layer6 = folium.GeoJson(NH6,style_function=lambda x:style7, name = 'Strafford County').add_to(NH_map)
    layer7 = folium.GeoJson(NH7,style_function=lambda x:style8, name = 'Carroll County').add_to(NH_map)
    FloatImage(img, bottom = 2, left = 88).add_to(NH_map)
    main = folium.FeatureGroup()
    FloatImage(img1, bottom = 0, left = 0).add_to(NH_map)
    folium.LayerControl().add_to(NH_map)
    with open('NH.csv', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            merrimack = False
            belknap = False
            if(row['pm2.5'] == '?'):
                    point = Point(float(row['longitude']),float(row['latitude']))
                    for features in NH['geometry']:
                        polygon = shape(NH['geometry'])
                        if polygon.contains(point):
                            layer.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 15, weight = 3, color = 'black', fill_color='grey', fill_opacity=1).add_child(folium.Popup("Name: " + row['name'] + "\n" + "pm2.5: " + '\n' + row['pm2.5'])).add_to(NH_map))
                            layer.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(4,9),html='<div style = "font-size: 10pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
            elif(float(row['pm2.5']) < 12):
                if(float(row['pm2.5']) < 10):
                    point = Point(float(row['longitude']),float(row['latitude']))
                    for features in NH2['geometry']:
                        polygon = shape(NH2['geometry'])
                        if polygon.contains(point):
                            layer2.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'green', fill_color='green', fill_opacity=1).add_child(folium.Popup("Name: " + row['name'] + "\n" + "pm2.5: " + '\n' + row['pm2.5'])).add_to(NH_map))
                            layer2.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(11,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH1['geometry']: 
                        polygon = shape(NH1['geometry'])
                        if polygon.contains(point):
                            layer1.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'green', fill_color='green', fill_opacity=1).add_child(folium.Popup("Name: " + row['name'] + "\n" + "pm2.5: " + '\n' + row['pm2.5'])).add_to(NH_map))
                            layer1.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(11,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH3['geometry']: 
                        polygon = shape(NH3['geometry'])
                        if polygon.contains(point):
                            layer3.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'green', fill_color='green', fill_opacity=1).add_child(folium.Popup("Name: " + row['name'] + "\n" + "pm2.5: " + '\n' + row['pm2.5'])).add_to(NH_map))
                            layer3.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(11,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH4['geometry']: 
                        polygon = shape(NH4['geometry'])
                        if polygon.contains(point):
                            layer4.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'green', fill_color='green', fill_opacity=1).add_child(folium.Popup("Name: " + row['name'] + "\n" + "pm2.5: " + '\n' + row['pm2.5'])).add_to(NH_map))
                            layer4.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(11,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH5['geometry']: 
                        polygon = shape(NH5['geometry'])
                        if polygon.contains(point):
                            layer5.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'green', fill_color='green', fill_opacity=1).add_child(folium.Popup("Name: " + row['name'] + "\n" + "pm2.5: " + '\n' + row['pm2.5'])).add_to(NH_map))
                            layer5.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(11,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                        #else:
                            #folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'green', fill_color='green', fill_opacity=1).add_child(folium.Popup("Name: " + row['name'] + "\n" + "pm2.5: " + '\n' + row['pm2.5'])).add_to(NH_map)
                            #folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(11,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map)
                else:
                    folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'green', fill_color='green', fill_opacity=1).add_child(folium.Popup("Name: " + row['name'] + "\n" + "pm2.5: " + '\n' + row['pm2.5'])).add_to(NH_map)
                    folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map)
            elif(float(row['pm2.5']) < 35.4):
                folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'yellow', fill_color='yellow', fill_opacity=1).add_child(folium.Popup("Name: " + row['name'] + "\n" + "pm2.5: " + '\n' + row['pm2.5'])).add_to(NH_map)
                folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: red;">%s</div>' % row['pm2.5'],)).add_to(NH_map)
            elif(float(row['pm2.5']) < 55.4):
                folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'orange', fill_color='orange', fill_opacity=1).add_child(folium.Popup("Name: " + row['name'] + "\n" + "pm2.5: " + '\n' + row['pm2.5'])).add_to(NH_map)
                folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map)
            elif(float(row['pm2.5']) < 150.4):
                if(float(row['pm2.5']) < 100):
                    folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'red', fill_color='red', fill_opacity=1).add_child(folium.Popup("Name: " + row['name'] + "\n" + "pm2.5: " + '\n' + row['pm2.5'])).add_to(NH_map)
                    folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map)
                else:
                    folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'red', fill_color='red', fill_opacity=1).add_child(folium.Popup("Name: " + row['name'] + "\n" + "pm2.5: " + '\n' + row['pm2.5'])).add_to(NH_map)
                    folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map)
            elif(float(row['pm2.5']) < 250.4):
                folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'purple', fill_color='purple', fill_opacity=1).add_child(folium.Popup("Name: " + row['name'] + "\n" + "pm2.5: " + '\n' + row['pm2.5'])).add_to(NH_map)
                folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map)
            elif(float(row['pm2.5']) > 250.5):
                folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'maroon', fill_color='maroon', fill_opacity=1).add_child(folium.Popup("Name: " + row['name'] + "\n" + "pm2.5: " + '\n' + row['pm2.5'])).add_to(NH_map)
                folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map)
        NH_map.save('nhPointMap.html')

def mapMaking():
    from folium.plugins import FloatImage
    from folium.plugins import MarkerCluster
    import json
    from shapely.geometry import shape, Point
    import PIL
    from PIL import Image
    #image_file = Image.open('Legend.png')
    #image_file.putalpha(210)
    #image_file = image_file.save("Legend.png")
    #img = 'Legend.png'
    image_file1 = Image.open('Colors.png')
    image_file1.putalpha(190)
    image_file1 = image_file1.save("Colors.png")
    img1 = 'Colors.png'
    with open('NH.geojson') as f:
        NH = json.load(f)
    with open('NHCounty.geojson') as r:
        NH1 = json.load(r)
    with open('NHCounty2.geojson') as j:
        NH2 = json.load(j)
    with open('NHCounty3.geojson') as l:
        NH3 = json.load(l)
    with open('NHCounty4.geojson') as p:
        NH4 = json.load(p)
    with open('NHCounty5.geojson') as t:
        NH5 = json.load(t)
    with open('NHCounty6.geojson') as z:
        NH6 = json.load(z)
    with open('NHCounty7.geojson') as k:
        NH7 = json.load(k)
    with open('NHCounty8.geojson') as kl:
        NH8 = json.load(kl)
    with open('NHCounty9.geojson') as klr:
        NH9 = json.load(klr)
    with open('NHCounty10.geojson') as klrz:
        NH10 = json.load(klrz)
    NH_map = folium.Map(location=[43.209568, -71.53729], zoom_start = 8, minZoom = 4, max_bounds = True)
    style1 = {'fillColor': '#e6e6fa', 'color': '#ba55d3', 'fillOpacity': 0.4}
    style2 = {'color': '#1e90ff', 'fillOpacity': 0.20}
    style3 = {'color': '#0077be', 'fillOpacity': 0.20}
    style4 = {'color': '#4682b4', 'fillOpacity': 0.20}
    style5 = {'color': '#006db0', 'fillOpacity': 0.20}
    style6 = {'color': '#0095b6', 'fillOpacity': 0.20}
    style7 = {'color': '#006994', 'fillOpacity': 0.20}
    style8 = {'color': '#0095b6', 'fillOpacity': 0.20}
    style9 = {'color': '#72a0c1', 'fillOpacity': 0.20}
    style10 = {'color': '#6ca0dc', 'fillOpacity': 0.20}
    style11 = {'color': '#5b92e5', 'fillOpacity': 0.20}
    layer = folium.GeoJson(NH,style_function=lambda x:style1, name = 'State Outline').add_to(NH_map)
    layer1 = folium.GeoJson(NH1,style_function=lambda x:style2, name = 'Belknap County').add_to(NH_map)
    layer7 = folium.GeoJson(NH7,style_function=lambda x:style8, name = 'Carroll County').add_to(NH_map)
    layer4 = folium.GeoJson(NH4,style_function=lambda x:style5, name = 'Cheshire County').add_to(NH_map)
    layer10 = folium.GeoJson(NH10,style_function=lambda x:style11, name = 'Coos County').add_to(NH_map)
    layer9 = folium.GeoJson(NH9,style_function=lambda x:style10, name = 'Grafton County').add_to(NH_map)
    layer3 = folium.GeoJson(NH3,style_function=lambda x:style4, name = 'Hillsborough County').add_to(NH_map)
    layer2 = folium.GeoJson(NH2,style_function=lambda x:style3, name = 'Merrimack County').add_to(NH_map)
    layer5 = folium.GeoJson(NH5,style_function=lambda x:style6, name = 'Rockingham County').add_to(NH_map)
    layer6 = folium.GeoJson(NH6,style_function=lambda x:style7, name = 'Strafford County').add_to(NH_map)
    layer8 = folium.GeoJson(NH8,style_function=lambda x:style9, name = 'Sullivan County').add_to(NH_map)
    layer1.add_child(folium.Popup('Belknap County')).add_to(NH_map)
    layer2.add_child(folium.Popup('Merrimack County')).add_to(NH_map)
    layer3.add_child(folium.Popup('Hillsborough County')).add_to(NH_map)
    layer4.add_child(folium.Popup('Cheshire County')).add_to(NH_map)
    layer5.add_child(folium.Popup('Rockingham County')).add_to(NH_map)
    layer6.add_child(folium.Popup('Strafford County')).add_to(NH_map)
    layer7.add_child(folium.Popup('Carroll County')).add_to(NH_map)
    layer8.add_child(folium.Popup('Sullivan County')).add_to(NH_map)
    layer9.add_child(folium.Popup('Grafton County')).add_to(NH_map)
    layer10.add_child(folium.Popup('Coos County')).add_to(NH_map)
    #FloatImage(img, bottom = 2, left = 88).add_to(NH_map)
    main = folium.FeatureGroup()
    FloatImage(img1, bottom = 0, left = 0).add_to(NH_map)
    folium.LayerControl().add_to(NH_map)
    with open('NH.csv', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            merrimack = False
            belknap = False
            if(row['pm2.5'] == '?'):
                    point = Point(float(row['longitude']),float(row['latitude']))
                    for features in NH['geometry']:
                        polygon = shape(NH['geometry'])
                        if polygon.contains(point):
                            layer.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 15, weight = 2, color = 'black', fill_color='grey', fill_opacity=1).add_child(folium.Popup("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(4,9),html='<div style = "font-size: 10pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
            elif(float(row['pm2.5']) < 12):
                if(float(row['pm2.5']) < 10):
                    point = Point(float(row['longitude']),float(row['latitude']))
                    for features in NH2['geometry']:
                        polygon = shape(NH2['geometry'])
                        if polygon.contains(point):
                            layer2.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'green', fill_color='green', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer2.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(11,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH1['geometry']: 
                        polygon = shape(NH1['geometry'])
                        if polygon.contains(point):
                            layer1.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'green', fill_color='green', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer1.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(11,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH3['geometry']: 
                        polygon = shape(NH3['geometry'])
                        if polygon.contains(point):
                            layer3.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'green', fill_color='green', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer3.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(11,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH4['geometry']: 
                        polygon = shape(NH4['geometry'])
                        if polygon.contains(point):
                            layer4.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'green', fill_color='green', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer4.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(11,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH5['geometry']: 
                        polygon = shape(NH5['geometry'])
                        if polygon.contains(point):
                            layer5.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'green', fill_color='green', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer5.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(11,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH6['geometry']: 
                        polygon = shape(NH6['geometry'])
                        if polygon.contains(point):
                            layer6.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'green', fill_color='green', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer6.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(11,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH7['geometry']: 
                        polygon = shape(NH7['geometry'])
                        if polygon.contains(point):
                            layer7.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'green', fill_color='green', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer7.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(11,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH8['geometry']: 
                        polygon = shape(NH8['geometry'])
                        if polygon.contains(point):
                            layer8.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'green', fill_color='green', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer8.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(11,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH9['geometry']: 
                        polygon = shape(NH9['geometry'])
                        if polygon.contains(point):
                            layer9.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'green', fill_color='green', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer9.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(11,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH10['geometry']: 
                        polygon = shape(NH10['geometry'])
                        if polygon.contains(point):
                            layer10.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'green', fill_color='green', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer10.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(11,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                        #else:
                            #folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'green', fill_color='green', fill_opacity=1).add_child(folium.Popup("Name: " + row['name'] + "\n" + "pm2.5: " + '\n' + row['pm2.5'])).add_to(NH_map)
                            #folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(11,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map)
                else:
                    point = Point(float(row['longitude']),float(row['latitude']))
                    for features in NH2['geometry']:
                        polygon = shape(NH2['geometry'])
                        if polygon.contains(point):
                            layer2.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'green', fill_color='green', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer2.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH1['geometry']:
                        polygon = shape(NH1['geometry'])
                        if polygon.contains(point):
                            layer1.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'green', fill_color='green', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer1.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH3['geometry']:
                        polygon = shape(NH3['geometry'])
                        if polygon.contains(point):
                            layer3.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'green', fill_color='green', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer3.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH4['geometry']:
                        polygon = shape(NH4['geometry'])
                        if polygon.contains(point):
                            layer4.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'green', fill_color='green', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer4.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH5['geometry']:
                        polygon = shape(NH5['geometry'])
                        if polygon.contains(point):
                            layer5.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'green', fill_color='green', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer5.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH6['geometry']:
                        polygon = shape(NH6['geometry'])
                        if polygon.contains(point):
                            layer6.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'green', fill_color='green', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer6.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH7['geometry']:
                        polygon = shape(NH7['geometry'])
                        if polygon.contains(point):
                            layer7.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'green', fill_color='green', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer7.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH8['geometry']:
                        polygon = shape(NH8['geometry'])
                        if polygon.contains(point):
                            layer8.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'green', fill_color='green', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer8.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH9['geometry']:
                        polygon = shape(NH9['geometry'])
                        if polygon.contains(point):
                            layer9.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'green', fill_color='green', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer9.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH10['geometry']:
                        polygon = shape(NH10['geometry'])
                        if polygon.contains(point):
                            layer10.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'green', fill_color='green', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer10.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
            elif(float(row['pm2.5']) < 35.4):
                    point = Point(float(row['longitude']),float(row['latitude']))
                    for features in NH2['geometry']:
                        polygon = shape(NH2['geometry'])
                        if polygon.contains(point):
                            layer2.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'yellow', fill_color='yellow', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer2.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: red;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH1['geometry']:
                        polygon = shape(NH1['geometry'])
                        if polygon.contains(point):
                            layer1.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'yellow', fill_color='yellow', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer1.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: red;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH3['geometry']:
                        polygon = shape(NH3['geometry'])
                        if polygon.contains(point):
                            layer3.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'yellow', fill_color='yellow', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer3.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: red;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH4['geometry']:
                        polygon = shape(NH4['geometry'])
                        if polygon.contains(point):
                            layer4.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'yellow', fill_color='yellow', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer4.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: red;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH5['geometry']:
                        polygon = shape(NH5['geometry'])
                        if polygon.contains(point):
                            layer5.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'yellow', fill_color='yellow', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer5.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: red;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH6['geometry']:
                        polygon = shape(NH6['geometry'])
                        if polygon.contains(point):
                            layer6.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'yellow', fill_color='yellow', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer6.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: red;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH7['geometry']:
                        polygon = shape(NH7['geometry'])
                        if polygon.contains(point):
                            layer7.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'yellow', fill_color='yellow', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer7.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: red;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH8['geometry']:
                        polygon = shape(NH8['geometry'])
                        if polygon.contains(point):
                            layer8.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'yellow', fill_color='yellow', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer8.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: red;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH9['geometry']:
                        polygon = shape(NH9['geometry'])
                        if polygon.contains(point):
                            layer9.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'yellow', fill_color='yellow', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer9.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: red;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH10['geometry']:
                        polygon = shape(NH10['geometry'])
                        if polygon.contains(point):
                            layer10.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'yellow', fill_color='yellow', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer10.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: red;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
            elif(float(row['pm2.5']) < 55.4):
                    point = Point(float(row['longitude']),float(row['latitude']))
                    for features in NH2['geometry']:
                        polygon = shape(NH2['geometry'])
                        if polygon.contains(point):
                            layer2.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'orange', fill_color='orange', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer2.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH1['geometry']:
                        polygon = shape(NH1['geometry'])
                        if polygon.contains(point):
                            layer1.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'orange', fill_color='orange', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer1.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH3['geometry']:
                        polygon = shape(NH3['geometry'])
                        if polygon.contains(point):
                            layer3.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'orange', fill_color='orange', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer3.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH4['geometry']:
                        polygon = shape(NH4['geometry'])
                        if polygon.contains(point):
                            layer4.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'orange', fill_color='orange', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer4.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH5['geometry']:
                        polygon = shape(NH5['geometry'])
                        if polygon.contains(point):
                            layer5.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'orange', fill_color='orange', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer5.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH6['geometry']:
                        polygon = shape(NH6['geometry'])
                        if polygon.contains(point):
                            layer6.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'orange', fill_color='orange', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer6.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH7['geometry']:
                        polygon = shape(NH7['geometry'])
                        if polygon.contains(point):
                            layer7.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'orange', fill_color='orange', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer7.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH8['geometry']:
                        polygon = shape(NH8['geometry'])
                        if polygon.contains(point):
                            layer8.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'orange', fill_color='orange', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer8.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH9['geometry']:
                        polygon = shape(NH9['geometry'])
                        if polygon.contains(point):
                            layer9.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'orange', fill_color='orange', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer9.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH10['geometry']:
                        polygon = shape(NH10['geometry'])
                        if polygon.contains(point):
                            layer10.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'orange', fill_color='orange', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer10.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
            elif(float(row['pm2.5']) < 150.4):
                if(float(row['pm2.5']) < 100):
                    point = Point(float(row['longitude']),float(row['latitude']))
                    for features in NH2['geometry']:
                        polygon = shape(NH2['geometry'])
                        if polygon.contains(point):
                            layer2.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'red', fill_color='red', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer2.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH1['geometry']:
                        polygon = shape(NH1['geometry'])
                        if polygon.contains(point):
                            layer1.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'red', fill_color='red', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer1.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH3['geometry']:
                        polygon = shape(NH3['geometry'])
                        if polygon.contains(point):
                            layer3.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'red', fill_color='red', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer3.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH4['geometry']:
                        polygon = shape(NH4['geometry'])
                        if polygon.contains(point):
                            layer4.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'red', fill_color='red', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer4.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH5['geometry']:
                        polygon = shape(NH5['geometry'])
                        if polygon.contains(point):
                            layer5.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'red', fill_color='red', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer5.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH6['geometry']:
                        polygon = shape(NH6['geometry'])
                        if polygon.contains(point):
                            layer6.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'red', fill_color='red', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5:" + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer6.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH7['geometry']:
                        polygon = shape(NH7['geometry'])
                        if polygon.contains(point):
                            layer7.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'red', fill_color='red', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer7.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH8['geometry']:
                        polygon = shape(NH8['geometry'])
                        if polygon.contains(point):
                            layer8.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'red', fill_color='red', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer8.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH9['geometry']:
                        polygon = shape(NH9['geometry'])
                        if polygon.contains(point):
                            layer9.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'red', fill_color='red', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer9.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                    for features in NH10['geometry']:
                        polygon = shape(NH10['geometry'])
                        if polygon.contains(point):
                            layer10.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'red', fill_color='red', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer10.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(13,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
                else:
                    point = Point(float(row['longitude']),float(row['latitude']))
                    for features in NH2['geometry']:
                        polygon = shape(NH2['geometry'])
                        if polygon.contains(point):
                            layer2.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'red', fill_color='red', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer2.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))                    
                    for features in NH1['geometry']:
                        polygon = shape(NH1['geometry'])
                        if polygon.contains(point):
                            layer1.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'red', fill_color='red', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer1.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))                    
                    for features in NH3['geometry']:
                        polygon = shape(NH3['geometry'])
                        if polygon.contains(point):
                            layer3.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'red', fill_color='red', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer3.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))                    
                    for features in NH4['geometry']:
                        polygon = shape(NH4['geometry'])
                        if polygon.contains(point):
                            layer4.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'red', fill_color='red', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer4.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))                    
                    for features in NH5['geometry']:
                        polygon = shape(NH5['geometry'])
                        if polygon.contains(point):
                            layer5.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'red', fill_color='red', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer5.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))                    
                    for features in NH6['geometry']:
                        polygon = shape(NH6['geometry'])
                        if polygon.contains(point):
                            layer6.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'red', fill_color='red', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer6.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))                    
                    for features in NH7['geometry']:
                        polygon = shape(NH7['geometry'])
                        if polygon.contains(point):
                            layer7.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'red', fill_color='red', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer7.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))                    
                    for features in NH8['geometry']:
                        polygon = shape(NH8['geometry'])
                        if polygon.contains(point):
                            layer8.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'red', fill_color='red', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer8.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))                    
                    for features in NH9['geometry']:
                        polygon = shape(NH9['geometry'])
                        if polygon.contains(point):
                            layer9.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'red', fill_color='red', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer9.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))                    
                    for features in NH10['geometry']:
                        polygon = shape(NH10['geometry'])
                        if polygon.contains(point):
                            layer10.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'red', fill_color='red', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer10.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
            elif(float(row['pm2.5']) < 250.4):
                    point = Point(float(row['longitude']),float(row['latitude']))
                    for features in NH2['geometry']:
                        polygon = shape(NH2['geometry'])
                        if polygon.contains(point):
                            layer2.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'purple', fill_color='purple', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer2.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))                    
                    for features in NH1['geometry']:
                        polygon = shape(NH1['geometry'])
                        if polygon.contains(point):
                            layer1.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'purple', fill_color='purple', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer1.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))                    
                    for features in NH3['geometry']:
                        polygon = shape(NH3['geometry'])
                        if polygon.contains(point):
                            layer3.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'purple', fill_color='purple', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer3.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))                    
                    for features in NH4['geometry']:
                        polygon = shape(NH4['geometry'])
                        if polygon.contains(point):
                            layer4.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'purple', fill_color='purple', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer4.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))                    
                    for features in NH5['geometry']:
                        polygon = shape(NH5['geometry'])
                        if polygon.contains(point):
                            layer5.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'purple', fill_color='purple', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer5.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))                    
                    for features in NH6['geometry']:
                        polygon = shape(NH6['geometry'])
                        if polygon.contains(point):
                            layer6.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'purple', fill_color='purple', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer6.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))                    
                    for features in NH7['geometry']:
                        polygon = shape(NH7['geometry'])
                        if polygon.contains(point):
                            layer7.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'purple', fill_color='purple', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer7.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))                    
                    for features in NH8['geometry']:
                        polygon = shape(NH8['geometry'])
                        if polygon.contains(point):
                            layer8.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'purple', fill_color='purple', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer8.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))                    
                    for features in NH9['geometry']:
                        polygon = shape(NH9['geometry'])
                        if polygon.contains(point):
                            layer9.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'purple', fill_color='purple', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer9.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))                    
                    for features in NH10['geometry']:
                        polygon = shape(NH10['geometry'])
                        if polygon.contains(point):
                            layer10.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'purple', fill_color='purple', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer10.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
            elif(float(row['pm2.5']) > 250.5):
                    point = Point(float(row['longitude']),float(row['latitude']))
                    for features in NH2['geometry']:
                        polygon = shape(NH2['geometry'])
                        if polygon.contains(point):
                            layer2.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'maroon', fill_color='maroon', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer2.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))                    
                    for features in NH1['geometry']:
                        polygon = shape(NH1['geometry'])
                        if polygon.contains(point):
                            layer1.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'maroon', fill_color='maroon', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer1.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))                    
                    for features in NH3['geometry']:
                        polygon = shape(NH3['geometry'])
                        if polygon.contains(point):
                            layer3.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'maroon', fill_color='maroon', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer3.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))                    
                    for features in NH4['geometry']:
                        polygon = shape(NH4['geometry'])
                        if polygon.contains(point):
                            layer4.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'maroon', fill_color='maroon', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer4.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))                    
                    for features in NH5['geometry']:
                        polygon = shape(NH5['geometry'])
                        if polygon.contains(point):
                            layer5.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'maroon', fill_color='maroon', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer5.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))                    
                    for features in NH6['geometry']:
                        polygon = shape(NH6['geometry'])
                        if polygon.contains(point):
                            layer6.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'maroon', fill_color='maroon', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer6.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))                    
                    for features in NH7['geometry']:
                        polygon = shape(NH7['geometry'])
                        if polygon.contains(point):
                            layer7.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'maroon', fill_color='maroon', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer7.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))                    
                    for features in NH8['geometry']:
                        polygon = shape(NH8['geometry'])
                        if polygon.contains(point):
                            layer8.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'maroon', fill_color='maroon', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer8.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))                    
                    for features in NH9['geometry']:
                        polygon = shape(NH9['geometry'])
                        if polygon.contains(point):
                            layer9.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'maroon', fill_color='maroon', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer9.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))                    
                    for features in NH10['geometry']:
                        polygon = shape(NH10['geometry'])
                        if polygon.contains(point):
                            layer10.add_child(folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'maroon', fill_color='maroon', fill_opacity=1).add_child(folium.Tooltip("Name: " + row['name'] + "\n" + "PM2.5: " + '\n' + row['pm2.5'] + ' µg/m3')).add_to(NH_map))
                            layer10.add_child(folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(16,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map))
        NH_map.save('nhPointMap.html')
        file = open('nhPointMap.html', 'r')
        file2 = open('temporary.html', 'w')
        count = 0
        trap = 0
        thing = r'{"attribution": "\u0026copy; \u003ca href=\"http://openstreetmap.org\"\u003eOpenStreetMap\u003c/a\u003e | \u003ca href=\"http://www.des.nh.gov\"\u003eNHDES\u003c/a\u003e | \u003ca href=\"http://www2.purpleair.com\"\u003ePurpleAir\u003c/a\u003e", "detectRetina": false, "maxNativeZoom": 18, "maxZoom": 18, "minZoom": 0, "noWrap": false, "opacity": 1, "subdomains": "abc", "tms": false}'
        thing2 = r'<link rel = "icon" href = "th.png">'
        thing3 = r'<title> Purple Air | NH  Department of Environmental &#173; &#173; &#173; &#173; &#173; Services </title>'
        thing4 = '\u003c\u0021\u002d\u002d ' + r'0100100101100110001000000111010001101000011010010111001100100000011011010110010101110011011100110110000101100111011001010010000001101001011100110010000001100110011011110111010101101110011001000010000001100001011011100110010000100000011001000110010101100011011010010111000001101000011001010111001001100101011001000010110000100000011110010110111101110101001000000110011001101111011101010110111001100100001000000111010001101000011001010010000001100001011101010111010001101000011011110111001001100000011100110010000001101110011011110111010001100101001011100010000001000100011000010111010001100101011001000010000000110000001110000010111100110001001100010010111100110010001100000011001000110010001000000100000000100000001100010011000100111010001100110011000100100000010000010100110100100000011000100111100100100000010110100110000101100011011010000110000101110010011110010010000001100000010101000100011101100000001000000101010001101000011011110111001001101111011101010110011101101000011001110110111101101111011001000010000001100001011011000110111101101110011001110010000001110111011010010111010001101000001000000100001101101000011000010111001101100101001011000010000001001101011000010111001001100011011101010111001100101110001011000010000001000101011100100111001001101001011011100110011101110100011011110110111000101100001000000100101101100001011101000110100001101100011001010110010101101110001011100010110000100000010010000110010101100001011011000111100100101100001000000100010001100001011101100110100101100100001011100010110000100000011000010110111001100100001000000101010101101110011001000110010101110010011010000110100101101100011011000010110000100000010010100110010101100110011001100010111000100000010101110110100101110100011010000010000001100001001000000111001101110000011001010110001101101001011000010110110000100000011101000110100001100001011011100110101101110011001000000111010001101111001000000100010001110010001011100010000001010100011100100110000101110110011010010111001101110011001011000010000001001010010000110010110000100000011000010110111001100100001000000100100001100001011100110111010001101001011011100110011101110011001011000010000001010111011010010110110001101100011010010110000101101101001000000110000101101011011000010010000001000111011001010110111101110010011001110110010100101110' + ' \u002d\u002d\u003e'
        while True:
            count += 1
            line = file.readline()
            if not line:
                break
            elif line.__contains__('http-equiv'):
                file2.writelines(line + '\n\t\t' + thing3 + '\n\t\t' + thing2 + '\n\t\t' + thing4)
                trap = count
            elif line.__contains__('"attribution"'):
                file2.writelines('\t\t\t\t' + thing + '\n')
                trap = count
            else:
                file2.write(line)
        file.close()
        file2.close()
        
        file = open('nhPointMap.html', 'w')
        file2 = open('temporary.html', 'r')
        count = 0
        while True:
            count += 1
            line = file2.readline()
            if not line:
                break
            else:
                file.writelines(line)
        file.close()
        file2.close()
        os.remove("temporary.html")

def createCSV(jsonObject, jsonObject1, jsonObject2, jsonObject3, jsonObject4, bool):
    try:
        arrayKeys = []
        for keys in keywords.split(','):
            arrayKeys.append(keys)
        keyIndex = []
        duplicateSpecify = []
        turn = 0
        for dups in duplicates.split(':'):
            if(turn == 0):
                keyIndex.append(dups)
                turn = 1
            else:
                duplicateSpecify.append(dups)
                turn = 0
        logging.info('Starting the createCSV() method')
        repeat = 0
        repeat_a = 0
        repeat_b = 0
        repeat_c = 0
        if bool == False:
            arrayValues = []
            csvcurrentfile = open('DESPurple' + Datee + '.csv', 'w', newline = '')
            csvcurrent = csv.writer(csvcurrentfile)
            csvcurrent.writerow(arrayKeys)
            try:
                index = -1
                dict_1 = False;
                dict_2 = False;
                dict_3 = False;
                dict_4 = False;
                dict_5 = False;
                for i in arrayKeys:
                    index = index + 1
                    clock = 0
                    try: 
                        try:
                            if((i in keyIndex) == True):
                                temps = helpme(jsonObject, jsonObject1, jsonObject2, jsonObject3, jsonObject4, i, keyIndex, duplicateSpecify)
                                arrayValues.append(temps)
                                clock = 1
                                continue
                        except:
                            pass
                        if(clock != 1 and str(jsonObject.get(i)) != 'None' and dict_1 == False):
                            if(i == "time_stamp"):
                                temporary = jsonObject.get(i)
                                d = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S')) 
                                arrayValues.append(d)
                                continue
                            elif(i == "data_time_stamp"):
                                temporary = jsonObject.get(i)
                                d = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S')) 
                                arrayValues.append(d)
                                dict_1 = True
                                clock = 1
                                continue
                            else:
                                temporary = str(jsonObject.get(i))
                                arrayValues.append(temporary)
                                clock = 1
                                continue
                    except:
                        pass
                    try: 
                        if(clock != 1 and str(jsonObject1.get(i)) != 'None' and dict_2 == False):
                            if(i == "last_modified" or i == "date_created" or i == "last_seen"):
                                temporary = jsonObject1.get(i)
                                d = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S')) 
                                arrayValues.append(d)
                                continue
                            elif(i == "secondary_key_b"):
                                temporary = str(jsonObject1.get(i))
                                arrayValues.append(temporary)
                                clock = 1
                                dict_2 = True
                                continue
                            else:
                                temporary = str(jsonObject1.get(i))
                                arrayValues.append(temporary)
                                clock = 1
                                continue
                    except:
                        pass
                    try:
                        if(clock != 1 and str(jsonObject2.get(i)) != 'None' and dict_3 == False):
                            if(i == "time_stamp"):
                                temporary = jsonObject2.get(i)
                                d = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S')) 
                                arrayValues.append(d)
                                dict_3 = True
                                clock = 1
                                continue
                            else:
                                temporary = str(jsonObject2.get(i))
                                arrayValues.append(temporary)
                                clock = 1
                                continue
                    except:
                        pass
                    try:
                        if(clock != 1 and str(jsonObject3.get(i)) != 'None' and dict_4 == False):
                            if(i == "time_stamp"):
                                temporary = jsonObject3.get(i)
                                d = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S')) 
                                arrayValues.append(d)
                                dict_4 = True
                                clock = 1
                                continue
                            else:
                                temporary = str(jsonObject3.get(i))
                                arrayValues.append(temporary)
                                clock = 1
                                continue
                    except:
                        pass
                    try:
                        if(clock != 1 and str(jsonObject4.get(i)) != 'None' and dict_5 == False):
                            if(i == "time_stamp"):
                                temporary = jsonObject4.get(i)
                                d = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S')) 
                                arrayValues.append(d)
                                dict_5 = True
                                clock = 1
                                continue
                            else:
                                temporary = str(jsonObject4.get(i))
                                arrayValues.append(temporary)
                                clock = 1
                                continue
                        elif(i == "stats" or i == "stats_a" or i == "stats_b" or i == "sensor"):
                            temporary = ''
                            arrayValues.append(temporary)
                        elif(i == "Time Executed"):
                            temporary = Timez
                            d = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S')) 
                            arrayValues.append(d)
                        elif(i == "pm2.5_10minute_a"):
                            temporary = jsonObject3.get("pm2.5_10minute")
                            arrayValues.append(temporary)
                        elif(i == "pm2.5_10minute_b"):
                            temporary = jsonObject4.get("pm2.5_10minute")
                            arrayValues.append(temporary)
                        elif(i == "PM2.5_Diff"):
                            temporary_a = jsonObject3.get("pm2.5_10minute")
                            temporary_b = jsonObject4.get("pm2.5_10minute")
                            value = abs(temporary_a - temporary_b)
                            value = round(value, 2)
                            arrayValues.append(value)
                        elif(i == "PM2.5_RelDiff"):
                            try:
                                temporary_a = jsonObject3.get("pm2.5_10minute")
                                temporary_b = jsonObject4.get("pm2.5_10minute")
                                value_mean = float(temporary_a - temporary_b)
                                value_sum = float((temporary_a + temporary_b) / 2)
                                value_final = float((value_mean / value_sum) * 100) 
                                value_final = round(abs(value_final),0)
                                arrayValues.append(str(value_final))
                            except:
                                if(value_sum == 0):
                                    logging.error("Division by zero")
                                    arrayValues.append(0)
                        elif(i =="PM2.5_JumpA"):
                            try:
                                num_a = ''
                                jump_a = ''
                                with open('DESPurple' + Datee + '.csv', 'r') as f:
                                    readingz = csv.DictReader(f, delimiter=",")
                                    rowz = list(readingz)
                                    current_index = jsonObject1.get('sensor_index')
                                    for row in reversed(rowz):
                                        if(str(current_index) == row['sensor_index']):
                                            jump_a = row['pm2.5_10minute_a']
                                            break
                                    num_a = jsonObject3.get("pm2.5_10minute")
                                    ending = abs(float(jump_a) - float(num_a))
                                    ending = round(ending, 2)
                                    arrayValues.append(str(ending))
                                f.close()
                            except:
                                logging.info("Must be the first iteration for the day!")
                                arrayValues.append(0)
                        elif(i =="PM2.5_JumpB"):
                            try:
                                jump_b = ''
                                num_b = ''
                                with open('DESPurple' + Datee + '.csv', 'r') as f:
                                    readingz = csv.DictReader(f, delimiter=",")
                                    rowz = list(readingz)
                                    current_index = jsonObject1.get('sensor_index')
                                    for row in reversed(rowz):
                                        if(str(current_index) == row['sensor_index']):
                                            jump_b = row['pm2.5_10minute_b']
                                            break
                                    num_b = jsonObject4.get("pm2.5_10minute")
                                    ending = abs(float(jump_b) - float(num_b))
                                    ending = round(ending, 2)
                                    arrayValues.append(str(ending))
                                f.close()
                            except:
                                logging.info("Must be the first iteration for the day!")
                                arrayValues.append(0)
                        elif(i =="PM2.5_JumpRelDiff"):
                            try:
                                jump_a_index = arrayKeys.index("PM2.5_JumpA")
                                jump_b_index = arrayKeys.index("PM2.5_JumpB")
                                temporary_a = float(arrayValues[jump_a_index])
                                temporary_b = float(arrayValues[jump_b_index])
                                value_mean = (temporary_a - temporary_b)
                                value_sum = ((temporary_a + temporary_b) / 2)
                                value_final = round((abs(float(value_mean) / float(value_sum)) * 100),0)
                                arrayValues.append(value_final)
                            except:
                                if(value_sum == 0):
                                    logging.error("Division by zero")
                                    arrayValues.append(0)
                        elif(i == "RH_Diff"):
                            humidity_a_index = arrayKeys.index("humidity_a")
                            humidity_b_index = arrayKeys.index("humidity_b")
                            RH_A = arrayValues[humidity_a_index]
                            RH_B = arrayValues[humidity_b_index]
                            temporary = abs(float(RH_A) - float(RH_B))
                            arrayValues.append(temporary)
                        elif(i == "RH_JumpA"):
                            try:
                                RHjump_a = ''
                                num_a = ''
                                with open('DESPurple' + Datee + '.csv', 'r') as f:
                                    readingz = csv.DictReader(f, delimiter=",")
                                    rowz = list(readingz)
                                    current_index = jsonObject1.get('sensor_index')
                                    for row in reversed(rowz):
                                        if(str(current_index) == row['sensor_index']):
                                            RHjump_a = row['humidity_a']
                                            break
                                    num_a = jsonObject2.get("humidity_a")
                                    ending = abs(float(RHjump_a) - float(num_a))
                                    ending = round(ending, 2)
                                    arrayValues.append(str(ending))
                                f.close()
                            except:
                                logging.info("Must be the first iteration for the day!")
                                arrayValues.append(0)
                        elif(i == "RH_JumpB"):
                            try:
                                RHjump_b = ''
                                num_b = ''
                                with open('DESPurple' + Datee + '.csv', 'r') as f:
                                    readingz = csv.DictReader(f, delimiter=",")
                                    rowz = list(readingz)
                                    current_index = jsonObject1.get('sensor_index')
                                    for row in reversed(rowz):
                                        if(str(current_index) == row['sensor_index']):
                                            RHjump_b = row['humidity_b']
                                            break
                                    num_b = jsonObject2.get("humidity_b")
                                    ending = abs(float(RHjump_b) - float(num_b))
                                    ending = round(ending, 2)
                                    arrayValues.append(str(ending))
                                f.close()
                            except:
                                logging.info("Must be the first iteration for the day!")
                                arrayValues.append(0)
                        elif(i == "RH_JumpDiff"):
                            RHhumidity_a_index = arrayKeys.index("RH_JumpA")
                            RHhumidity_b_index = arrayKeys.index("RH_JumpB")
                            RH_A = arrayValues[RHhumidity_a_index]
                            RH_B = arrayValues[RHhumidity_b_index]
                            temporary = abs(float(RH_A) - float(RH_B))
                            arrayValues.append(temporary)
                        elif(i =="PM2.5 QA Flag"):
                            RD_threshold = 125
                            rd_threshold = 50
                            A_threshold = 7
                            B_threshold = 7
                            Diff_threshold = 10
                            time_threshold = 3
                            jump_a_index = arrayKeys.index("PM2.5_JumpA")
                            jump_b_index = arrayKeys.index("PM2.5_JumpB")
                            jump_rd_index = arrayKeys.index("PM2.5_JumpRelDiff")
                            chan_a_index = arrayKeys.index("pm2.5_10minute_a")
                            chan_b_index = arrayKeys.index("pm2.5_10minute_b")
                            channel_a = arrayValues[chan_a_index]
                            channel_b = arrayValues[chan_b_index]
                            jump_a = arrayValues[jump_a_index]
                            jump_b = arrayValues[jump_b_index]
                            jump_rd = arrayValues[jump_rd_index]
                            value = ''
                            guard = False
                            time_index = arrayKeys.index("Time Executed")
                            time = arrayValues[time_index]
                            last_time_index = arrayKeys.index("last_seen")
                            last_time = arrayValues[last_time_index]
                            timez = abs(Timez - jsonObject1.get('last_seen'))
                            timez = float((timez) / 60)
                            timez = round(timez,2)
                            if(timez >= time_threshold):
                                guard = True
                                value = "T"
                                arrayValues.append(value)
                            elif(float(channel_a) == 0 and float(channel_b) == 0 and guard == False):
                                guard = True
                                value = "ZAB"
                                arrayValues.append(value)
                            elif(float(channel_a) == 0 and float(channel_b) != 0 and guard == False):
                                guard = True
                                value = "ZA"
                                arrayValues.append(value)
                            elif(float(channel_a) != 0 and float(channel_b) == 0 and guard == False):
                                guard = True
                                value = "ZB"
                                arrayValues.append(value)
                            elif(float(jump_rd) > float(RD_threshold) and float(jump_a) > float(A_threshold) and float(jump_b) <= float(B_threshold) and guard == False):
                                value = 'JA'
                                guard = True
                                arrayValues.append(value)
                            elif(float(jump_rd) > float(RD_threshold) and float(jump_a) <= float(A_threshold) and float(jump_b) > float(B_threshold) and guard == False):
                                value = 'JB'
                                guard = True
                                arrayValues.append(value)
                            else:
                                try:
                                    jump_qa = ''
                                    with open('DESPurple' + Datee + '.csv', 'r') as f:
                                        readingz = csv.DictReader(f, delimiter=",")
                                        rowz = list(readingz)
                                        current_index = jsonObject1.get('sensor_index')
                                        for row in reversed(rowz):
                                            if(str(current_index) == row['sensor_index']):
                                                jump_qa = row['PM2.5 QA Flag']
                                                break
                                    f.close()
                                    diff_index = arrayKeys.index("PM2.5_Diff")
                                    rd_index = arrayKeys.index("PM2.5_RelDiff")
                                    diff = arrayValues[diff_index]
                                    rd = arrayValues[rd_index]
                                    if(jump_qa == 'JA' and float(jump_b) < float(B_threshold) and float(rd) > float(rd_threshold) and float(diff) > float(Diff_threshold) and guard == False):
                                        value = 'JA'
                                        guard = True
                                        arrayValues.append(value)
                                    elif(jump_qa == 'JB' and float(jump_a) < float(A_threshold) and float(rd) > float(rd_threshold) and float(diff) > float(Diff_threshold) and guard == False):
                                        value = 'JB'
                                        guard = True
                                        arrayValues.append(value)  
                                    elif(float(diff) > float(Diff_threshold) and float(rd) > float(rd_threshold) and guard == False):
                                        value = 'QQ'
                                        guard = True
                                        arrayValues.append(value)                                     
                                    elif(guard == False):
                                        temporary = 'Passed'
                                        arrayValues.append(temporary)
                                except:
                                    logging.info("Means there was no previous PM2.5 QA Flag yet")
                                    temporary = 'Passed'
                                    arrayValues.append(temporary)
                                    pass
                        elif(i == "RH QA Flag"):
                            try:
                                RHDiff_threshold = 10
                                RHJumpDiff_threshold = 10
                                RH_A_index = arrayKeys.index("humidity_a")
                                RH_A = arrayValues[RH_A_index]
                                RH_B_index = arrayKeys.index("humidity_b")
                                RH_B = arrayValues[RH_B_index]
                                RH_JumpDiff_index = arrayKeys.index("RH_JumpDiff")
                                RH_JumpDiff = arrayValues[RH_JumpDiff_index]
                                RH_JumpA_index = arrayKeys.index("RH_JumpA")
                                RH_JumpA = arrayValues[RH_JumpA]
                                RH_JumpB_index = arrayKeys.index("RH_JumpB")
                                RH_JumpB = arrayValues[RH_JumpB]
                                RH_Diff_index = arrayKeys.index("RH_Diff")
                                RH_Diff = arrayValues[RH_Diff_index]
                                guard = False
                                value = ''
                                if(float(RH_A) == 0 and float(RH_B) == 0 and guard == False):
                                    guard = True
                                    value = "RHZAB"
                                    arrayValues.append(value)
                                elif(float(RH_A) == 0 and float(RH_B) != 0 and guard == False):
                                    guard = True
                                    value = "RHZA"
                                    arrayValues.append(value)
                                elif(float(RH_A) != 0 and float(RH_B) == 0 and guard == False):
                                    guard = True
                                    value = "RHZB"
                                    arrayValues.append(value)
                                elif(float(RH_JumpDiff) > float(RHJumpDiff_threshold) and abs(float(RH_JumpA)) <= float(RHJumpDiff_threshold) and abs(float(RH_JumpB)) > float(RHJumpDiff_threshold) and guard == False):
                                    value = 'RHJB'
                                    guard = True
                                    arrayValues.append(value)
                                elif(float(RH_JumpDiff) > float(RHJumpDiff_threshold) and abs(float(RH_JumpA)) > float(RHJumpDiff_threshold) and abs(float(RH_JumpB)) <= float(RHJumpDiff_threshold) and guard == False):
                                    value = 'RHJA'
                                    guard = True
                                    arrayValues.append(value)
                                elif(float(RH_Diff) > float(RHDiff_threshold) and guard == False):
                                    value = 'RHQQ'
                                    guard = True
                                    arrayValues.append(value)
                                elif(guard == False):
                                    temporary = 'Passed'
                                    arrayValues.append(temporary)
                            except:
                                logging.info("Means there was no previous RH QA Flag yet")
                                temporary = 'Passed'
                                arrayValues.append(temporary)
                                pass
                        elif(i == "RH Avg"):
                            qa_index = arrayKeys.index("RH QA Flag")
                            qa = arrayValues[qa_index]
                            RH_A_index = arrayKeys.index("humidity_a")
                            RH_A = arrayValues[RH_A_index]
                            RH_B_index = arrayKeys.index("humidity_b")
                            RH_B = arrayValues[RH_B_index]
                            guard = False
                            if(qa == "RHJA" or qa == "RHZA"):
                                arrayValues.append(RH_B)
                                guard = True
                            elif(qa == "RHJB" or qa == "RHZB" and guard == False):
                                arrayValues.append(RH_A)
                                guard = True
                            elif(qa == "RHZAB" or qa == "RHQQ" and guard == False):
                                arrayValues.append('')
                                guard = True
                            else:
                                average = ((float(RH_A) + float(RH_B)) / 2)
                                average = round(average, 1)
                                arrayValues.append(average)
                        elif(i == "PM2.5 Uncorrected Avg"):
                            a_index = arrayKeys.index("pm2.5_10minute_a")
                            b_index = arrayKeys.index("pm2.5_10minute_b")
                            qa_index = arrayKeys.index("PM2.5 QA Flag")
                            a = arrayValues[a_index]
                            b = arrayValues[b_index]
                            qa = arrayValues[qa_index]
                            if(qa == "JB"):
                                temporary = a
                                arrayValues.append(a)
                            elif(qa == "JA"):
                                temporary = b
                                arrayValues.append(b)
                            elif(qa == "Passed"):
                                average = ((float(a) + float(b)) / 2)
                                average = round(average, 2)
                                arrayValues.append(average)
                            elif(qa == "QQ" or qa == "ZA" or qa == "ZB" or qa == "ZAB" or qa == "T"):
                                temporary = ''
                                arrayValues.append(temporary)
                            else:
                                temporary = ''
                                arrayValues.append(temporary)
                        elif(i == "PM2.5 Corrected"):
                            qa_index = arrayKeys.index("PM2.5 QA Flag")
                            uncorrect_index = arrayKeys.index("PM2.5 Uncorrected Avg")
                            uncorrect = arrayValues[uncorrect_index]
                            humidity_index = arrayKeys.index("RH Avg")
                            qa = arrayValues[qa_index]
                            humidity = arrayValues[humidity_index]
                            lat_index = arrayKeys.index("latitude")
                            long_index = arrayKeys.index("longitude")
                            if(uncorrect == ''):
                                temporary = ''
                                value = '?'
                                arrayValues.append(temporary)
                                mapCSV(jsonObject1, value)
                            else:
                                final_value = round((((0.61 * float(uncorrect)) - (0.07 * float(humidity))) + 2.16),2)
                                arrayValues.append(final_value)
                                mapCSV(jsonObject1, final_value)
                        else:
                            if(i == "humidity_b"):
                                arrayValues.append(0)
                            else:
                                temporary = 'None'
                                arrayValues.append(temporary)
                    except:
                        pass
                        logging.info('If you get this message, your keyword of ' + i + ' does not exist in the json file.')
                    
                csvcurrent.writerow(arrayValues)
                csvcurrentfile.close()
            except:
                logging.error('Problem with finding the correct dictionary/key in a subsection of the JSON')
                logging.info('Examine the Json file for certain keywords you want and figure out which jsonObject holds the key(s) you want to grab')
                logging.info('Time of program exit ' + datetime.now().strftime('%m/%d/%Y %H:%M:%S'))
        elif bool == True:
            arrayValues = []
            try:
                index = -1
                dict_1 = False;
                dict_2 = False;
                dict_3 = False;
                dict_4 = False;
                dict_5 = False;
                for i in arrayKeys:
                    index = index + 1
                    clock = 0
                    try:
                        if((i in keyIndex) == True):
                            temps = helpme(jsonObject, jsonObject1, jsonObject2, jsonObject3, jsonObject4, i, keyIndex, duplicateSpecify)
                            arrayValues.append(temps)
                            clock = 1
                            continue
                    except:
                        pass
                    try:
                        if(clock != 1 and str(jsonObject.get(i)) != 'None' and dict_1 == False):
                            if(i == "time_stamp"):
                                temporary = jsonObject.get(i)
                                d = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S')) 
                                arrayValues.append(d)
                                continue
                            elif(i == "data_time_stamp"):
                                temporary = jsonObject.get(i)
                                d = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S')) 
                                arrayValues.append(d)
                                dict_1 = True
                                clock = 1
                                continue
                            else:
                                temporary = str(jsonObject.get(i))
                                arrayValues.append(temporary)
                                clock = 1
                                continue
                    except:
                        pass
                    try: 
                        if(clock != 1 and str(jsonObject1.get(i)) != 'None' and dict_2 == False):
                            if(i == "last_modified" or i == "date_created" or i == "last_seen"):
                                temporary = jsonObject1.get(i)
                                d = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S')) 
                                arrayValues.append(d)
                                continue
                            elif(i == "secondary_key_b"):
                                temporary = str(jsonObject1.get(i))
                                arrayValues.append(temporary)
                                clock = 1
                                dict_2 = True
                                continue
                            else:
                                temporary = str(jsonObject1.get(i))
                                arrayValues.append(temporary)
                                clock = 1
                                continue
                    except:
                        pass
                    try:
                        if(clock != 1 and str(jsonObject2.get(i)) != 'None' and dict_3 == False):
                            if(i == "time_stamp"):
                                temporary = jsonObject2.get(i)
                                d = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S')) 
                                arrayValues.append(d)
                                dict_3 = True
                                clock = 1
                                continue
                            else:
                                temporary = str(jsonObject2.get(i))
                                arrayValues.append(temporary)
                                clock = 1
                                continue
                    except:
                        pass
                    try:
                        if(clock != 1 and str(jsonObject3.get(i)) != 'None' and dict_4 == False):
                            if(i == "time_stamp"):
                                temporary = jsonObject3.get(i)
                                d = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S')) 
                                arrayValues.append(d)
                                dict_4 = True
                                clock = 1
                                continue
                            else:
                                temporary = str(jsonObject3.get(i))
                                arrayValues.append(temporary)
                                clock = 1
                                continue
                    except:
                        pass
                    try:
                        if(clock != 1 and str(jsonObject4.get(i)) != 'None' and dict_5 == False):
                            if(i == "time_stamp"):
                                temporary = jsonObject4.get(i)
                                d = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S')) 
                                arrayValues.append(d)
                                dict_5 = True
                                clock = 1
                                continue
                            else:
                                temporary = str(jsonObject4.get(i))
                                arrayValues.append(temporary)
                                clock = 1
                                continue
                        elif(i == "stats" or i == "stats_a" or i == "stats_b" or i == "sensor"):
                            temporary = ''
                            arrayValues.append(temporary)
                        elif(i == "Time Executed"):
                            temporary = Timez
                            d = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S')) 
                            arrayValues.append(d)
                        elif(i == "pm2.5_10minute_a"):
                            temporary = jsonObject3.get("pm2.5_10minute")
                            arrayValues.append(temporary)
                        elif(i == "pm2.5_10minute_b"):
                            temporary = jsonObject4.get("pm2.5_10minute")
                            arrayValues.append(temporary)
                        elif(i == "PM2.5_Diff"):
                            temporary_a = jsonObject3.get("pm2.5_10minute")
                            temporary_b = jsonObject4.get("pm2.5_10minute")
                            value = abs(temporary_a - temporary_b)
                            value = round(value, 2)
                            arrayValues.append(value)
                        elif(i == "PM2.5_RelDiff"):
                            try:
                                temporary_a = jsonObject3.get("pm2.5_10minute")
                                temporary_b = jsonObject4.get("pm2.5_10minute")
                                value_mean = float(temporary_a - temporary_b)
                                value_sum = float((temporary_a + temporary_b) / 2)
                                value_final = float((value_mean / value_sum) * 100) 
                                value_final = round(abs(value_final),0)
                                arrayValues.append(str(value_final))
                            except:
                                if(value_sum == 0):
                                    logging.error("Division by zero")
                                    arrayValues.append(0)
                        elif(i =="PM2.5_JumpA"):
                            try:
                                num_a = ''
                                jump_a = ''
                                with open('DESPurple' + Datee + '.csv', 'r') as f:
                                    readingz = csv.DictReader(f, delimiter=",")
                                    rowz = list(readingz)
                                    current_index = jsonObject1.get('sensor_index')
                                    for row in reversed(rowz):
                                        if(str(current_index) == row['sensor_index']):
                                            jump_a = row['pm2.5_10minute_a']
                                            break
                                    num_a = jsonObject3.get("pm2.5_10minute")
                                    ending = abs(float(jump_a) - float(num_a))
                                    ending = round(ending, 2)
                                    arrayValues.append(str(ending))
                                f.close()
                            except:
                                logging.info("Must be the first iteration for the day!")
                                arrayValues.append(0)
                        elif(i =="PM2.5_JumpB"):
                            try:
                                jump_b = ''
                                num_b = ''
                                with open('DESPurple' + Datee + '.csv', 'r') as f:
                                    readingz = csv.DictReader(f, delimiter=",")
                                    rowz = list(readingz)
                                    current_index = jsonObject1.get('sensor_index')
                                    for row in reversed(rowz):
                                        if(str(current_index) == row['sensor_index']):
                                            jump_b = row['pm2.5_10minute_b']
                                            break
                                    num_b = jsonObject4.get("pm2.5_10minute")
                                    ending = abs(float(jump_b) - float(num_b))
                                    ending = round(ending, 2)
                                    arrayValues.append(str(ending))
                                f.close()
                            except:
                                logging.info("Must be the first iteration for the day!")
                                arrayValues.append(0)
                        elif(i =="PM2.5_JumpRelDiff"):
                            try:
                                jump_a_index = arrayKeys.index("PM2.5_JumpA")
                                jump_b_index = arrayKeys.index("PM2.5_JumpB")
                                temporary_a = float(arrayValues[jump_a_index])
                                temporary_b = float(arrayValues[jump_b_index])
                                value_mean = (temporary_a - temporary_b)
                                value_sum = ((temporary_a + temporary_b) / 2)
                                value_final = round((abs(float(value_mean) / float(value_sum)) * 100),0)
                                arrayValues.append(value_final)
                            except:
                                if(value_sum == 0):
                                    logging.error("Division by zero")
                                    arrayValues.append(0)
                        elif(i == "RH_Diff"):
                            humidity_a_index = arrayKeys.index("humidity_a")
                            humidity_b_index = arrayKeys.index("humidity_b")
                            RH_A = arrayValues[humidity_a_index]
                            RH_B = arrayValues[humidity_b_index]
                            temporary = abs(float(RH_A) - float(RH_B))
                            arrayValues.append(temporary)
                        elif(i == "RH_JumpA"):
                            try:
                                RHjump_a = ''
                                num_a = ''
                                with open('DESPurple' + Datee + '.csv', 'r') as f:
                                    readingz = csv.DictReader(f, delimiter=",")
                                    rowz = list(readingz)
                                    current_index = jsonObject1.get('sensor_index')
                                    for row in reversed(rowz):
                                        if(str(current_index) == row['sensor_index']):
                                            RHjump_a = row['humidity_a']
                                            break
                                    num_a = jsonObject1.get("humidity_a")
                                    ending = abs(float(RHjump_a) - float(num_a))
                                    ending = round(ending, 2)
                                    arrayValues.append(str(ending))
                                f.close()
                            except:
                                logging.info("Must be the first iteration for the day!")
                                arrayValues.append(0)
                        elif(i == "RH_JumpB"):
                            try:
                                RHjump_b = ''
                                num_b = ''
                                with open('DESPurple' + Datee + '.csv', 'r') as f:
                                    readingz = csv.DictReader(f, delimiter=",")
                                    rowz = list(readingz)
                                    current_index = jsonObject1.get('sensor_index')
                                    for row in reversed(rowz):
                                        if(str(current_index) == row['sensor_index']):
                                            RHjump_b = row['humidity_b']
                                            break
                                    num_b = jsonObject1.get("humidity_b")
                                    ending = abs(float(RHjump_b) - float(num_b))
                                    ending = round(ending, 2)
                                    arrayValues.append(str(ending))
                                f.close()
                            except:
                                logging.info("Must be the first iteration for the day!")
                                arrayValues.append(0)
                        elif(i == "RH_JumpDiff"):
                            RHhumidity_a_index = arrayKeys.index("RH_JumpA")
                            RHhumidity_b_index = arrayKeys.index("RH_JumpB")
                            RH_A = arrayValues[RHhumidity_a_index]
                            RH_B = arrayValues[RHhumidity_b_index]
                            temporary = abs(float(RH_A) - float(RH_B))
                            arrayValues.append(temporary)
                        elif(i =="PM2.5 QA Flag"):
                            #print(jumpreldiffthreshold)
                            RD_threshold = jumpreldiffthreshold
                            #RD_threshold = 125
                            rd_threshold = 50
                            A_threshold = 7
                            B_threshold = 7
                            Diff_threshold = 10
                            time_threshold = 3
                            jump_a_index = arrayKeys.index("PM2.5_JumpA")
                            jump_b_index = arrayKeys.index("PM2.5_JumpB")
                            jump_rd_index = arrayKeys.index("PM2.5_JumpRelDiff")
                            chan_a_index = arrayKeys.index("pm2.5_10minute_a")
                            chan_b_index = arrayKeys.index("pm2.5_10minute_b")
                            channel_a = arrayValues[chan_a_index]
                            channel_b = arrayValues[chan_b_index]
                            jump_a = arrayValues[jump_a_index]
                            jump_b = arrayValues[jump_b_index]
                            jump_rd = arrayValues[jump_rd_index]
                            value = ''
                            guard = False
                            time_index = arrayKeys.index("Time Executed")
                            time = arrayValues[time_index]
                            last_time_index = arrayKeys.index("last_seen")
                            last_time = arrayValues[last_time_index]
                            timez = abs(Timez - jsonObject1.get('last_seen'))
                            timez = float((timez) / 60)
                            timez = round(timez,2)
                            if(timez >= time_threshold):
                                guard = True
                                value = "T"
                                arrayValues.append(value)
                            elif(float(channel_a) == 0 and float(channel_b) == 0 and guard == False):
                                guard = True
                                value = "ZAB"
                                arrayValues.append(value)
                            elif(float(channel_a) == 0 and float(channel_b) != 0 and guard == False):
                                guard = True
                                value = "ZA"
                                arrayValues.append(value)
                            elif(float(channel_a) != 0 and float(channel_b) == 0 and guard == False):
                                guard = True
                                value = "ZB"
                                arrayValues.append(value)
                            elif(float(jump_rd) > float(RD_threshold) and float(jump_a) > float(A_threshold) and float(jump_b) <= float(B_threshold) and guard == False):
                                value = 'JA'
                                guard = True
                                arrayValues.append(value)
                            elif(float(jump_rd) > float(RD_threshold) and float(jump_a) <= float(A_threshold) and float(jump_b) > float(B_threshold) and guard == False):
                                value = 'JB'
                                guard = True
                                arrayValues.append(value)
                            else:
                                try:
                                    jump_qa = ''
                                    with open('DESPurple' + Datee + '.csv', 'r') as f:
                                        readingz = csv.DictReader(f, delimiter=",")
                                        rowz = list(readingz)
                                        current_index = jsonObject1.get('sensor_index')
                                        for row in reversed(rowz):
                                            if(str(current_index) == row['sensor_index']):
                                                jump_qa = row['PM2.5 QA Flag']
                                                break
                                    f.close()
                                    diff_index = arrayKeys.index("PM2.5_Diff")
                                    rd_index = arrayKeys.index("PM2.5_RelDiff")
                                    diff = arrayValues[diff_index]
                                    rd = arrayValues[rd_index]
                                    if(jump_qa == 'JA' and float(jump_b) < float(B_threshold) and float(rd) > float(rd_threshold) and float(diff) > float(Diff_threshold) and guard == False):
                                        value = 'JA'
                                        guard = True
                                        arrayValues.append(value)
                                    elif(jump_qa == 'JB' and float(jump_a) < float(A_threshold) and float(rd) > float(rd_threshold) and float(diff) > float(Diff_threshold) and guard == False):
                                        value = 'JB'
                                        guard = True
                                        arrayValues.append(value)  
                                    elif(float(diff) > float(Diff_threshold) and float(rd) > float(rd_threshold) and guard == False):
                                        value = 'QQ'
                                        guard = True
                                        arrayValues.append(value)                                     
                                    elif(guard == False):
                                        temporary = 'Passed'
                                        arrayValues.append(temporary)
                                except:
                                    logging.info("Means there was no previous PM2.5 QA Flag yet")
                                    temporary = 'Passed'
                                    arrayValues.append(temporary)
                                    pass
                        elif(i == "RH QA Flag"):
                            try:
                                RHDiff_threshold = 10
                                RHJumpDiff_threshold = 10
                                RH_A_index = arrayKeys.index("humidity_a")
                                RH_A = arrayValues[RH_A_index]
                                RH_B_index = arrayKeys.index("humidity_b")
                                RH_B = arrayValues[RH_B_index]
                                RH_JumpDiff_index = arrayKeys.index("RH_JumpDiff")
                                RH_JumpDiff = arrayValues[RH_JumpDiff_index]
                                RH_JumpA_index = arrayKeys.index("RH_JumpA")
                                RH_JumpA = arrayValues[RH_JumpA_index]
                                RH_JumpB_index = arrayKeys.index("RH_JumpB")
                                RH_JumpB = arrayValues[RH_JumpB_index]
                                RH_Diff_index = arrayKeys.index("RH_Diff")
                                RH_Diff = arrayValues[RH_Diff_index]
                                guard = False
                                value = ''
                                if(float(RH_A) == 0 and float(RH_B) == 0 and guard == False):
                                    guard = True
                                    value = "RHZAB"
                                    arrayValues.append(value)
                                elif(float(RH_A) == 0 and float(RH_B) != 0 and guard == False):
                                    guard = True
                                    value = "RHZA"
                                    arrayValues.append(value)
                                elif(float(RH_A) != 0 and float(RH_B) == 0 and guard == False):
                                    guard = True
                                    value = "RHZB"
                                    arrayValues.append(value)
                                elif(float(RH_JumpDiff) > float(RHJumpDiff_threshold) and abs(float(RH_JumpA)) <= float(RHJumpDiff_threshold) and abs(float(RH_JumpB)) > float(RHJumpDiff_threshold) and guard == False):
                                    value = 'RHJB'
                                    guard = True
                                    arrayValues.append(value)
                                elif(float(RH_JumpDiff) > float(RHJumpDiff_threshold) and abs(float(RH_JumpA)) > float(RHJumpDiff_threshold) and abs(float(RH_JumpB)) <= float(RHJumpDiff_threshold) and guard == False):
                                    value = 'RHJA'
                                    guard = True
                                    arrayValues.append(value)
                                elif(float(RH_Diff) > float(RHDiff_threshold) and guard == False):
                                    value = 'RHQQ'
                                    guard = True
                                    arrayValues.append(value)
                                elif(guard == False):
                                    temporary = 'Passed'
                                    arrayValues.append(temporary)
                            except:
                                logging.info("Means there was no previous RH QA Flag yet")
                                temporary = 'Passed'
                                arrayValues.append(temporary)
                                pass
                        elif(i == "RH Avg"):
                            qa_index = arrayKeys.index("RH QA Flag")
                            qa = arrayValues[qa_index]
                            RH_A_index = arrayKeys.index("humidity_a")
                            RH_A = arrayValues[RH_A_index]
                            RH_B_index = arrayKeys.index("humidity_b")
                            RH_B = arrayValues[RH_B_index]
                            guard = False
                            if(qa == "RHJA" or qa == "RHZA"):
                                arrayValues.append(RH_B)
                                guard = True
                            elif(qa == "RHJB" or qa == "RHZB" and guard == False):
                                arrayValues.append(RH_A)
                                guard = True
                            elif(qa == "RHZAB" or qa == "RHQQ" and guard == False):
                                arrayValues.append('')
                                guard = True
                            else:
                                average = ((float(RH_A) + float(RH_B)) / 2)
                                average = round(average, 1)
                                arrayValues.append(average)
                        elif(i == "PM2.5 Uncorrected Avg"):
                            a_index = arrayKeys.index("pm2.5_10minute_a")
                            b_index = arrayKeys.index("pm2.5_10minute_b")
                            qa_index = arrayKeys.index("PM2.5 QA Flag")
                            a = arrayValues[a_index]
                            b = arrayValues[b_index]
                            qa = arrayValues[qa_index]
                            if(qa == "JB"):
                                temporary = a
                                arrayValues.append(a)
                            elif(qa == "JA"):
                                temporary = b
                                arrayValues.append(b)
                            elif(qa == "Passed"):
                                average = ((float(a) + float(b)) / 2)
                                average = round(average, 2)
                                arrayValues.append(average)
                            elif(qa == "QQ" or qa == "ZA" or qa == "ZB" or qa == "ZAB" or qa == "T"):
                                temporary = ''
                                arrayValues.append(temporary)
                            else:
                                temporary = ''
                                arrayValues.append(temporary)
                        elif(i == "PM2.5 Corrected"):
                            qa_index = arrayKeys.index("PM2.5 QA Flag")
                            uncorrect_index = arrayKeys.index("PM2.5 Uncorrected Avg")
                            uncorrect = arrayValues[uncorrect_index]
                            humidity_index = arrayKeys.index("RH Avg")
                            qa = arrayValues[qa_index]
                            humidity = arrayValues[humidity_index]
                            lat_index = arrayKeys.index("latitude")
                            long_index = arrayKeys.index("longitude")
                            if(uncorrect == '' or humidity == ''):
                                temporary = ''
                                value = '?'
                                arrayValues.append(temporary)
                                mapCSV(jsonObject1, value)
                            else:
                                final_value = round((((0.61 * float(uncorrect)) - (0.07 * float(humidity))) + 2.16),2)
                                arrayValues.append(final_value)
                                mapCSV(jsonObject1, final_value)
                        else:
                            if(i == "humidity_b" or i == "humidity_a" or i == "temperature_a" or i == "temperature_b"):
                                arrayValues.append(0)
                            else:
                                temporary = ''
                                arrayValues.append(temporary)
                    except:
                        pass
                        logging.info('If you get this message, your keyword of ' + i + ' does not exist in the json file.')
                csvcurrentfile = open('DESPurple' + Datee + '.csv', 'a', newline = '')
                csv_writer = writer(csvcurrentfile)
                csv_writer.writerow(arrayValues)
                csvcurrentfile.close()
            except:
                logging.error('Problem with finding the correct dictionary/key in a subsection of the JSON')
                logging.info('Examine the Json file for certain keywords you want and figure out which jsonObject holds the key(s) you want to grab')
                logging.info('Time of program exit ' + datetime.now().strftime('%m/%d/%Y %H:%M:%S'))
    except:
        logging.error('Unexpected Error')
        logging.info('Time of program exit ' + datetime.now().strftime('%m/%d/%Y %H:%M:%S'))    
'''        
Main driver function
This function of Jsonmyhero() just calls both main helper methods of readIni and API that do the heavy lifting
'''
def Jsonmyhero():
    try: 
        readIni()
    except:
        logging.error('Error occured inside of readIni() method')
        logging.info('Time of program exit ' + datetime.now().strftime('%m/%d/%Y %H:%M:%S'))    
    try:
        API()
    except:
        logging.error('Error occured inside of API() method')
        logging.info('Time of program exit ' + datetime.now().strftime('%m/%d/%Y %H:%M:%S'))
#Main function for our program
def main():
    #Call to the main drive function
    Jsonmyhero()
    mapMaking()
    # WGH Addition 08082022
    os.remove('NH.csv')
    logging.info('Time of program completion ' + datetime.now().strftime('%m/%d/%Y %H:%M:%S'))
    logging.shutdown()
#Call to main function
main()
#This moves our log files to the log folder
shutil.move(fileLocation,desinationLocation)