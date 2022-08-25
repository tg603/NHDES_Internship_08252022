'''
These are the import packages used down inside my code. 
csv - Creates the comma seperated values file for us to put our data from the Json file into for analyizing
json - Is the JavaScript Object Notation file that will hold all the raw data from the PA Servers
datetime - Allows me to get current time stamps and allows me to convert the time stamps on the Json (Epoch time) to our regular localized time
urllib.request - Is a package that allows us to call the API servers that PA have for their monitors to report back to
configparser - Is a package that helps create the .ini file that we can read without hardcoding unit's into this program
The from's just call certain subsections of these packages for me to use for certain things later on inside of the code
'''
import csv, json, datetime, urllib.request, configparser, logging, os, shutil, geopy, pandas, folium
from math import sqrt
from datetime import datetime, date, timezone
from folium import plugins
from folium.features import DivIcon
from csv import writer
from geopy.geocoders import Nominatim
'''
This part right here simply creates a global variable of the current date for me to use as a stamp for the .CSV file name creation
Datee is the formatted time that I need for the file name. Check this out if you're confused on the .strftime part: https://www.w3schools.com/python/python_datetime.asp
'''
global currentDate
currentDate = date.today()
Datee = currentDate.strftime("%m%d%Y")
'''
Logging allows me to create a seperated log of everything that happens within my code without using print statements.
The big difference being that print statements aren't saved and there's no collection of them.
Logging will create and track everything I want logged into a file called Log followed by the date and time of the program execution
See URL if confused at all: https://www.geeksforgeeks.org/logging-in-python/
'''
logName = 'Log'+ str(datetime.now().strftime('Date%m%d%YTime%H%M %S')) + '.log'
fileLocation = 'C:\\Users\\zachary.t.thoroughgo\\DES\Demo\\' + logName
desinationLocation = 'C:\\Users\\zachary.t.thoroughgo\\DES\Demo\\Logs\\' + logName
logging.basicConfig(filename = logName, filemode = 'w',level=logging.INFO)
logging.info('Start timestamp for execution is: ' + datetime.now().strftime('%m/%d/%Y %H:%M:%S'))
logging.info('Starting the execution of program Pull')
'''
Now this is the start of the readIni() method and the purpose of this method is to help out the rest of the program
by creating an .ini file if it doesn't already exist or update it for us to look at later. The .ini is important because
it allows for us to change certain variables inside of this code without having to touch the code. Eveuntally, I do believe
I can put the 'Keyword'/'Values' inside of this .ini file instead of hardcoding them in the arrayKeys and arrayValues array's.
This is *NOTED* and will be looked at further down the line as I attempt to progress this code and project.
'''
def readIni():
    #Try and except as a saftey net to keep the code from breaking in error moments
    try:
        #Logging the start of this method
        logging.info('Starting readIni() method')
        #Local globalized variables that will be inside of the .ini file
        global api, units, keywords, duplicates
        #Holds the correct format and values for the .ini file
        defaults = {
        'api':  'True',
        'units': '',
        'keywords': '',
        'duplicates' : '',
        }
        #Config object holds the now parsed defaults list 
        config = configparser.ConfigParser(defaults,allow_no_value=True)
        #We add the section of 'Main' inside of the parsed config to maintain .ini correct syntax/format
        config.add_section('Main')
        #Try and except as a saftey net to keep the code from breaking in error moments
        try:
            #Logging that we're attempting the open of this .ini file
            logging.info('Trying to open .ini file to read')
            #Object of f is set to the opening of the 'Demo.ini' file in reading mode ('r')
            f = open ("Demo.ini", 'r')
            #If this works the code will continue and log that this file does indeed exist
            logging.info('File exists')
            #We read the file of 'Demo.ini' here given through the open portal object of config
            config.read_file(f)
            #Now we close the open portal and we have completed reading the 'Demo.ini' if it exists
            f.close()
        except:
            #Means to do nothing 
            pass
        #Object of f is set to the opening of the 'Demo.ini' file in writing mode ('w')
        f = open ("Demo.ini", 'w')
        #We log that we're populating the .ini file now; if it exists nothing will change, if this is a new file it will add the default format
        logging.info('Populating .ini file now')
        #Write to the open .ini file using the object of config again
        config.write(f)
        #Assigns the value of items as the collection of values/keys inside of the .ini file or default created
        items = {x[0]:x[1] for x in config.items('Main')}
        #Assigns the values into their respective spots for the .ini file
        api         = items['api'] == 'True'
        units       = str(items['units'])
        keywords    = str(items['keywords'])
        duplicates    =str(items['duplicates'])
        #We log that we're finished executing this method
        logging.info('Finishing readIni() method')
    except:
        #Log whenever this method error's out and if it does it's not because of an anticipated error I could foresee
        logging.error('Unexpected Error')
        #We log the time of the program exit to signal the error time and that the program had errored out
        logging.info('Time of program exit ' + datetime.now().strftime('%m/%d/%Y %H:%M:%S'))        
'''
The API() Method:   
Calls the api server
loads Json file
dumps it into our .json file
Unsticks each subsection to their own Json object
returns each subsectioned Json Object with each dictionary (keys and values) for writing our .csv
'''   
def API():
    #Try and except as a saftey net to keep the code from breaking in error moments
    try:
        #Logging the start of this method
        amount = 0
        for number_unit in units.split('|'):
            amount = amount + 1
        logging.info('Starting API() method')
        #For loop that calls each unit individually inside of the .ini file and each unit should be seperated in there by the character '|' Example: units = 143456|151702|1224
        mapCSVCreate()
        for unit in units.split('|'):
            #Try and except as a saftey net to keep the code from breaking in error moments        
            try:
                #Object of out is assigned to the opening of the Json file 'DemoAPI.json' with the intentions of writing ('w')
                out = open (unit+"API.json","w")
                #We log the current unit being calling  
                logging.info("Unit is " + unit)
                #This url object is assigned to the portal that gives us the Json from any available PurpleAir; *NOTED* inside the api_key=<YOUR OWN KEY> we are currently using Keene States and we'll need our own
                url = "https://june2022.api.purpleair.com/v1/sensors/%s"\
                        "?api_key=DB310998-0207-11ED-8561-42010A800005" % (unit)
                #Object of f is set to the opening of the url
                f = urllib.request.urlopen (url)
            except:
                #Logs the current unit we're trying to pull from the API server
                logging.error('Unit is: ' + unit)
                #Logs are self explanitory
                logging.info('If blank, fill in the .ini file, save, and rerun program')
                logging.info('If unit ID is not blank, problem with connection to unit; either wrong ID or unit is down')
                #We log the time of the program exit to signal the error time and that the program had errored out
                logging.info('Time of program exit ' + datetime.now().strftime('%m/%d/%Y %H:%M:%S'))
            #Object of buffer is set to the raw data given in through the server by the object portal of f
            buff = f.read(); f.close()
            #Object of j is set to the loading of the raw data into the format of a json file
            j = json.loads(buff)
            #We dump the json formatted data into out which is our open .json file and give it a nice indentation of 2 for visually clearer results
            json.dump(j, out, indent = 2)
            #We have all the data we need so now we close out
            out.close() 
            #Here we essentially reopen out; we may not need to but it's something I'll look into later *NOTED*
            k = open(unit+'API.json')
            #We set the object of collection to the loading of our json file given through the open portal of k
            collection = json.load(k)
            #strdata is just the object of collection turned into a string for printing purposes; this will be taken out in later drafts *NOTED*
            strdata = str(collection)
            #All four of these jsonData's hold the keys/values (dictionary's) for each subsection of the json file that k has
            #Each is found by jumping into the first section of 'sensor' and then using that jump point to leap into the other subsections of the json file to get those dictionaries
            jsonData1 = collection["sensor"]
            jsonData2 = jsonData1["stats"]
            jsonData3 = jsonData1["stats_a"]
            jsonData4 = jsonData1["stats_b"]
            #We then reclose the json portal of k, again *sigh*
            k.close()
            #Now we make a call to the method of checkToC() which should return whether the .CSV exists yet or not; which tells us whether it's the beginning of the pull day or not
            exists = checkToC()
            #We're logging whether the .CSV exists or not
            logging.info('The .CSV file exists currently: ' + str(exists))
            #We pass now all the dictionaries from the Json file and the boolean of whether this .csv exists to the .csv creation method
            createCSV(collection, jsonData1, jsonData2, jsonData3, jsonData4, exists, amount)
            #mapCSV(jsonData1)
        #Here we log that we're done executing the API() method
        logging.info('Finishing API() method')
    except:
        #Log whenever this method error's out and if it does it's not because of an anticipated error I could foresee
        logging.error('Unexpected Error')
        #We log the time of the program exit to signal the error time and that the program had errored out
        logging.info('Time of program exit ' + datetime.now().strftime('%m/%d/%Y %H:%M:%S'))
'''
This method of checkToC() is simply used to tell us whether the .CSV file is created yet or not.
'''  
def checkToC():
    #Try and except as a saftey net to keep the code from breaking in error moments
    try:
        #The object of csvcurrentfile is dedicated to the opening of the .csv file in reading mode ('r')
        csvcurrentfile = open('DESPurple' + Datee + '.csv', 'r')
        #If it can open; it will continue the code here and we can now say that this file does already exists and set the boolean of exists to true
        exists = True
        #We log that the .CSV is already made 
        logging.info('.CSV is already made for todays pulling')
        #We'll return our boolean value
        return exists
    except:
        #We log that the .csv doesn't exist yet because it error when trying to open
        logging.info('.CSV hasnt been made yet for todays pulling')
        #We set the boolean value of exists to false
        exists = False
        #We return our boolean value
        return exists
def helpme(jsonObject, jsonObject1, jsonObject2, jsonObject3, jsonObject4, i, keyIndex, duplicateSpecify):
    spot = keyIndex.index(i)
    number = str(duplicateSpecify[spot])
    keyIndex[spot] = ''
    #print("number is :" + number)
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
            #print(temporary)
            value = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S'))
            return value
        else:
            value = str(jsonObject4.get(i))
            return value
    return value
    
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
        print(i)
        if(minimum > dist[i]):
            minimum = dist[i]
    #print("Minimum mileage is: " + str(minimum))
    index = dist.index(minimum)
    #print("done")
    #print("work")
    '''
    webUrl = requests.get('https://www.aviationweather.gov/metar/data?ids=KAFN&format=decoded&hours=0&taf=off&layout=on')
    web_Contents = webUrl.content
    print(web_Contents)
    #txt_writer = writer(currentfile)
    array_web = []
    for i in webUrl:
        data = str(webUrl.readline())
    '''
    #webUrl = urllib.request.urlopen('view-source:https://www.aviationweather.gov/metar/data?ids=KAFN&format=decoded&hours=0&taf=off&layout=on')
    #print("work")
    '''
    array_web = []
    for i in webUrl:
        data = str(web_Contents.readline())
        print(data)
        if(data.__contains__("RH")):
            print(data.find('RH'))
            temp = (data[124] + data[125])
            array_web.append(temp)
        #array_web.append(webUrl.readline())
        #currentfile.writelines(webUrl.readline())
    '''
    '''
    KAFN Airport in Jaffrey, NH
    '''
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
def mapMaking():
    from folium.plugins import FloatImage
    from folium.plugins import MarkerCluster
    image_file = 'Legend.png'
    with open('NH.geojson') as f:
        NH = json.load(f)
    with open('NHCounty.geojson') as r:
        NH1 = json.load(r)
    with open('NHCounty2.geojson') as j:
        NH2 = json.load(j)
    NH_map = folium.Map(location=[43.209568, -71.53729], zoom_start = 9)
    style1 = {'fillColor': '#e6e6fa', 'color': '#ba55d3', 'fillOpacity': 0.4}
    style2 = {'color': '#ff0000', 'fillOpacity': 0.20}
    style3 = {'color': '#002366', 'fillOpacity': 0.20}
    folium.GeoJson(NH,style_function=lambda x:style1).add_to(NH_map)
    folium.GeoJson(NH1,style_function=lambda x:style2).add_to(NH_map)
    folium.GeoJson(NH2,style_function=lambda x:style3).add_to(NH_map)
    FloatImage(image_file, bottom = 0, left = 85).add_to(NH_map)
    #marker_clust = MarkerCluster().add_to(NH_map)
    with open('NH.csv', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if(row['pm2.5'] == 'Fix'):
                    folium.CircleMarker((row['latitude'],row['longitude']), radius = 15, weight = 3, color = 'red', fill_color='white', fill_opacity=1).add_child(folium.Popup("Name: " + row['name'] + "\n" + "pm2.5: " + '\n' + row['pm2.5'])).add_to(NH_map)
                    folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(8,9),html='<div style = "font-size: 8pt; color: black;">%s</div>' % row['pm2.5'],)).add_to(NH_map)
            elif(float(row['pm2.5']) < 12):
                if(float(row['pm2.5']) < 10):
                    #folium.CircleMarker((row['latitude'],row['longitude']), radius = 15, weight = 2, color = 'maroon', fill_color='maroon', fill_opacity=1).add_child(folium.Popup("Name: " + row['name'] + "\n" + "pm2.5: " + '\n' + row['pm2.5'])).add_to(NH_map)
                    #folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(9,10),html='<div style = "font-size: 10pt; color: white;">%s</div>' % 255.67,)).add_to(NH_map)
                    folium.CircleMarker((row['latitude'],row['longitude']), radius = 20, weight = 2, color = 'green', fill_color='green', fill_opacity=1).add_child(folium.Popup("Name: " + row['name'] + "\n" + "pm2.5: " + '\n' + row['pm2.5'])).add_to(NH_map)
                    folium.map.Marker([float(row['latitude']), float(row['longitude'])], icon = DivIcon(icon_size=(15,15),icon_anchor=(11,10),html='<div style = "font-size: 8pt; color: white;">%s</div>' % row['pm2.5'],)).add_to(NH_map)
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

'''
    New_Hampshire = gpd.read_file('C:/Users/zachary.t.thoroughgo/DES/Environment/cb_2018_33_place_500k/cb_2018_33_place_500k.shp')
    print(str(New_Hampshire))
'''
'''
The method of createCSV() takes in the four json dictionaries that we've pulled inside of the API()
and the boolean that tells us whether we need to create a new .csv or append to the one already in existance.
This method pulls the information needed given from the hardcoded arrays and grabs those keys from the dictionary
objects that it corresponds/lands inside of. 
'''  
def createCSV(jsonObject, jsonObject1, jsonObject2, jsonObject3, jsonObject4, bool, amount):
    #Try and except as a saftey net to keep the code from breaking in error moments
    try:
        arrayKeys = []
        #arrayKeys = SaveMyFingers(jsonObject, jsonObject1, jsonObject2, jsonObject3, jsonObject4)
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
        #print(str(keyIndex))
        #print(str(duplicateSpecify))
        #We log that we're starting the method of createCSV()
        logging.info('Starting the createCSV() method')
        #A conditional if statement asks if bool is false which means that we'll need to create a brand new .csv file today with the correct header
        repeat = 0
        repeat_a = 0
        repeat_b = 0
        repeat_c = 0
        if bool == False:
            #These arrays hold the Key's and the ready to be filled values we'll pull from the dicitionary objects
            #arrayKeys = ["data_time_stamp","humidity","sensor_index", "name", "pm1.0", "pm1.0_a", "pm1.0_b","pm2.5", "pm2.5_a", "pm2.5_b", "pm10.0", "pm10.0_a", "pm10.0_b"]
            arrayValues = []
            #Here we open the .csv file and use the write mode of ('w') to create a brand new file
            csvcurrentfile = open('DESPurple' + Datee + '.csv', 'w', newline = '')
            #Print hey show's we're working; I'll need to take it out later *NOTED*
            #print("Hey")
            #Here we call the csv.writer and use it on the open portal and assign it to the object of csvcurrent
            csvcurrent = csv.writer(csvcurrentfile)
            #We can use this writer object of csvcurrent to write the header which is just all the values inside of the arrayKeys array
            csvcurrent.writerow(arrayKeys)
            #Try and except as a saftey net to keep the code from breaking in error moments
            try:
                index = -1
                dict_1 = False;
                dict_2 = False;
                dict_3 = False;
                dict_4 = False;
                dict_5 = False;
                #For loop goes through arrayKeys and i is each value being iterated through
                for i in arrayKeys:
                    index = index + 1
                    clock = 0
                    '''
                    #This conditional if looks for the "data_time_stamp" that is special because it needs to be converted from epoch
                    if(i == "data_time_stamp" or i == "time_stamp"):
                        #We assign the value of temporary to the epoch value found when given the key through our json dicitionary object
                        temporary = jsonObject.get(i)
                        #We set the string value of d equal to the string of the datetime converting our temporary and formatting it with strftime to fit our needs
                        d = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S')) 
                        #We now put that into our array of values
                        arrayValues.append(d)
                    #Else will include everything else because they require zero conversions
                    else:
                    '''
                    try: 
                        #print("i is: " + i)
                        #print(dict_1)
                        #print(dict_2)
                        #print(dict_3)
                        #print(dict_4)
                        #print(dict_5)
                        try:
                            if((i in keyIndex) == True):
                                temps = helpme(jsonObject, jsonObject1, jsonObject2, jsonObject3, jsonObject4, i, keyIndex, duplicateSpecify)
                                #print(temps)
                                arrayValues.append(temps)
                                #print(arrayValues)
                                clock = 1
                                continue
                        except:
                            pass
                        if(clock != 1 and str(jsonObject.get(i)) != 'None' and dict_1 == False):
                            if(i == "time_stamp"):
                                #We assign the value of temporary to the epoch value found when given the key through our json dicitionary object
                                temporary = jsonObject.get(i)
                                #We set the string value of d equal to the string of the datetime converting our temporary and formatting it with strftime to fit our needs
                                d = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S')) 
                                #We now put that into our array of values
                                arrayValues.append(d)
                                continue
                            elif(i == "data_time_stamp"):
                                #We assign the value of temporary to the epoch value found when given the key through our json dicitionary object
                                temporary = jsonObject.get(i)
                                #We set the string value of d equal to the string of the datetime converting our temporary and formatting it with strftime to fit our needs
                                d = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S')) 
                                #We now put that into our array of values
                                arrayValues.append(d)
                                dict_1 = True
                                clock = 1
                                continue
                            else:
                                #We assign the value found by giving our key into the dicitionary object and convert it to a string
                                #print(i)
                                temporary = str(jsonObject.get(i))
                                #We then add this string value to our array of values
                                arrayValues.append(temporary)
                                clock = 1
                                continue
                    except:
                        pass
                    try: 
                        if(clock != 1 and str(jsonObject1.get(i)) != 'None' and dict_2 == False):
                            if(i == "last_modified" or i == "date_created" or i == "last_seen"):
                                #We assign the value of temporary to the epoch value found when given the key through our json dicitionary object
                                temporary = jsonObject1.get(i)
                                #We set the string value of d equal to the string of the datetime converting our temporary and formatting it with strftime to fit our needs
                                d = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S')) 
                                #We now put that into our array of values
                                arrayValues.append(d)
                                continue
                            elif(i == "secondary_key_b"):
                                #We assign the value found by giving our key into the dicitionary object and convert it to a string
                                #print(i)
                                temporary = str(jsonObject1.get(i))
                                #We then add this string value to our array of values
                                arrayValues.append(temporary)
                                clock = 1
                                dict_2 = True
                                continue
                            else:
                                #We assign the value found by giving our key into the dicitionary object and convert it to a string
                                #print(i)
                                temporary = str(jsonObject1.get(i))
                                #We then add this string value to our array of values
                                arrayValues.append(temporary)
                                clock = 1
                                continue
                    except:
                        pass
                    try:
                        if(clock != 1 and str(jsonObject2.get(i)) != 'None' and dict_3 == False):
                            if(i == "time_stamp"):
                                #We assign the value of temporary to the epoch value found when given the key through our json dicitionary object
                                temporary = jsonObject2.get(i)
                                #We set the string value of d equal to the string of the datetime converting our temporary and formatting it with strftime to fit our needs
                                d = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S')) 
                                #We now put that into our array of values
                                arrayValues.append(d)
                                dict_3 = True
                                clock = 1
                                continue
                            else:
                                #We assign the value found by giving our key into the dicitionary object and convert it to a string
                                #print(i)
                                temporary = str(jsonObject2.get(i))
                                #We then add this string value to our array of values
                                arrayValues.append(temporary)
                                clock = 1
                                continue
                    except:
                        pass
                    try:
                        if(clock != 1 and str(jsonObject3.get(i)) != 'None' and dict_4 == False):
                            if(i == "time_stamp"):
                                #We assign the value of temporary to the epoch value found when given the key through our json dicitionary object
                                temporary = jsonObject3.get(i)
                                #We set the string value of d equal to the string of the datetime converting our temporary and formatting it with strftime to fit our needs
                                d = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S')) 
                                #We now put that into our array of values
                                arrayValues.append(d)
                                dict_4 = True
                                clock = 1
                                continue
                            else:
                                #We assign the value found by giving our key into the dicitionary object and convert it to a string
                                #print(i)
                                temporary = str(jsonObject3.get(i))
                                #We then add this string value to our array of values
                                arrayValues.append(temporary)
                                clock = 1
                                continue
                    except:
                        pass
                    try:
                        if(clock != 1 and str(jsonObject4.get(i)) != 'None' and dict_5 == False):
                            if(i == "time_stamp"):
                                #We assign the value of temporary to the epoch value found when given the key through our json dicitionary object
                                temporary = jsonObject4.get(i)
                                #We set the string value of d equal to the string of the datetime converting our temporary and formatting it with strftime to fit our needs
                                d = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S')) 
                                #We now put that into our array of values
                                arrayValues.append(d)
                                dict_5 = True
                                clock = 1
                                continue
                            else:
                                #We assign the value found by giving our key into the dicitionary object and convert it to a string
                                #print(i)
                                temporary = str(jsonObject4.get(i))
                                #We then add this string value to our array of values
                                arrayValues.append(temporary)
                                clock = 1
                                continue
                        elif(i == "stats" or i == "stats_a" or i == "stats_b" or i == "sensor" or i == "channel a" or i == "channel b"):
                            temporary = ''
                            arrayValues.append(temporary)
                        elif(i == "Location"):
                            temp_long = jsonObject1.get("longitude")
                            #print(temp_long)
                            temp_lat = jsonObject1.get("latitude")
                            #print(temp_lat)
                            loco = locationz(temp_long, temp_lat)
                            arrayValues.append(loco)
                            #print(loco['city'])
                            clock = 1
                        #Channel A 10 minute average
                        elif(i == "A"):
                            temporary = jsonObject3.get("pm2.5_10minute")
                            arrayValues.append(temporary)
                        #Channel B 10 minute average
                        elif(i == "B"):
                            temporary = jsonObject4.get("pm2.5_10minute")
                            arrayValues.append(temporary)
                        #Difference between channel A and B
                        elif(i == "Diff"):
                            temporary_a = jsonObject3.get("pm2.5_10minute")
                            temporary_b = jsonObject4.get("pm2.5_10minute")
                            value = abs(temporary_a - temporary_b)
                            value = round(value, 2)
                            arrayValues.append(value)
                        #Standard Deviation 
                        elif(i == "Rel Dif"):
                            temporary_a = jsonObject3.get("pm2.5_10minute")
                            temporary_b = jsonObject4.get("pm2.5_10minute")
                            value_mean = float(temporary_a - temporary_b)
                            #value_sum = ((temporary_a - value_mean) ** 2) + ((temporary_b - value_mean) ** 2)
                            value_sum = float((temporary_a + temporary_b) / 2)
                            value_final = float((value_mean / value_sum) * 100) 
                            value_final = round(value_final,0)
                            arrayValues.append(value_final)
                        elif(i =="JumpA"):
                            try:
                                #current_row = 0
                                #clockz = -1
                                #timer = 0
                                num_a = ''
                                jump_a = ''
                                #with open('DESPurple' + Datee + '.csv', 'r') as f:
                                    #reader = csv.reader(f, delimiter="\t")
                                    #for k, line in enumerate(reader):
                                        #current_row = k
                                        #print('line[{}] = {}'.format(k,line))
                                #f.close()
                                with open('DESPurple' + Datee + '.csv', 'r') as f:
                                    readingz = csv.DictReader(f, delimiter=",")
                                    rowz = list(readingz)
                                    #first = 0
                                    current_index = jsonObject1.get('sensor_index')
                                    for row in reversed(rowz):
                                        #if(first == 0):
                                            #current_index = row['sensor_index']
                                        #clockz = clockz + 1
                                        #if(clockz == (current_row - amount)):
                                        if(str(current_index) == row['sensor_index']):
                                            print(row['sensor_index'])
                                            jump_a = row['A']
                                            print(row['A'])
                                            break
                                            #arrayValues.append(row['A'])
                                        #first = 1 
                                    '''
                                    for rowing in rowz:
                                        print("Thing " + str(current_row - timer))
                                        timer = timer + 1                                    
                                        if(0 == (current_row - timer)):
                                            num_a = rowing['A']
                                            print(rowing['A'])
                                    '''
                                    num_a = jsonObject3.get("pm2.5_10minute")
                                    print("First number: " + str(num_a))
                                    print("Second number: " + jump_a)
                                    ending = abs(float(jump_a) - float(num_a))
                                    ending = round(ending, 2)
                                    print("End value: " + str(ending))
                                    arrayValues.append(str(ending))
                                    #print(arrayValues)
                                f.close()
                                #print("This row is: " + str(current_row))
                            except:
                                logging.info("Must be the first iteration for the day!")
                                arrayValues.append(0)
                                #print(amount)
                        elif(i =="JumpB"):
                            try:
                                #current_row = 0
                                #clockz = -1
                                jump_b = ''
                                num_b = ''
                                #with open('DESPurple' + Datee + '.csv', 'r') as f:
                                    #reader = csv.reader(f, delimiter="\t")
                                    #for k, line in enumerate(reader):
                                        #current_row = k
                                        #print('line[{}] = {}'.format(k,line))
                                #f.close()
                                with open('DESPurple' + Datee + '.csv', 'r') as f:
                                    readingz = csv.DictReader(f, delimiter=",")
                                    rowz = list(readingz)
                                    current_index = jsonObject1.get('sensor_index')
                                    for row in reversed(rowz):
                                        #clockz = clockz + 1
                                        #if(clockz == (current_row - amount)):
                                            #jump_b = row['B']
                                            #arrayValues.append(row['B'])
                                        if(str(current_index) == row['sensor_index']):
                                            print(row['sensor_index'])
                                            jump_b = row['B']
                                            print(row['B'])
                                            break
                                    num_b = jsonObject4.get("pm2.5_10minute")
                                    print("2First number: " + str(num_b))
                                    print("2Second number: " + jump_b)
                                    ending = abs(float(jump_b) - float(num_b))
                                    ending = round(ending, 2)
                                    print("2End value: " + str(ending))
                                    arrayValues.append(str(ending))
                                    #print(arrayValues)
                                #f.close()
                                #print("This row is: " + str(current_row))
                                #print(amount)
                                f.close()
                                #print("This row is: " + str(current_row))
                            except:
                                logging.info("Must be the first iteration for the day!")
                                arrayValues.append(0)
                        elif(i =="JumpSD"):
                            #print(str(arrayKeys.index("JumpA")))
                            #print(str(arrayKeys.index("JumpB")))
                            jump_a_index = arrayKeys.index("JumpA")
                            jump_b_index = arrayKeys.index("JumpB")
                            temporary_a = float(arrayValues[jump_a_index])
                            temporary_b = float(arrayValues[jump_b_index])
                            #print(str(temporary_a))
                            #print(str(temporary_b))
                            value_mean = ((temporary_a + temporary_b) / 2)
                            value_sum = ((temporary_a - value_mean) ** 2) + ((temporary_b - value_mean) ** 2)
                            #print("hey there")
                            value_final = float(sqrt((1/2) * value_sum))
                            arrayValues.append(value_final)
                        elif(i =="Q&A"):
                            #variables for tests
                            RD_threshold = 125
                            #EPA one
                            rd_threshold = 50
                            A_threshold = 7
                            B_threshold = 7
                            Diff_threshold = 10
                            #Four Tests
                            jump_a_index = arrayKeys.index("JumpA")
                            jump_b_index = arrayKeys.index("JumpB")
                            jump_sd_index = arrayKeys.index("JumpSD")
                            humidity_index = arrayKeys.index("humidity")
                            jump_a = arrayValues[jump_a_index]
                            print("jumpa " + str(jump_a))
                            jump_b = arrayValues[jump_b_index]
                            print(arrayKeys)
                            jump_sd = arrayValues[jump_sd_index]
                            humidity = arrayValues[humidity_index]
                            value = ''
                            guard = False
                            #Test 1
                            #Initiates when Jump_a is bigger than the threshold
                            #print(jump_sd)
                            #print("Yahooooo")
                            if(float(jump_sd) > float(RD_threshold) and float(jump_a) > float(A_threshold) and float(jump_b) <= float(B_threshold)):
                                #print("Yehaw")
                                if(humidity == "None"):
                                    value = "JARH"
                                    guard = True
                                    arrayValues.append(value)
                                else:
                                    value = 'JA'
                                    guard = True
                                    arrayValues.append(value)
                            #Initiates when Jump_b is bigger than the threshold
                            elif(float(jump_sd) > float(RD_threshold) and float(jump_a) <= float(A_threshold) and float(jump_b) > float(B_threshold)):
                                #print("horse")
                                if(humidity == "None"):
                                    value = "JBRH"
                                    guard = True
                                    arrayValues.append(value)  
                                else:
                                    value = 'JB'
                                    guard = True
                                    arrayValues.append(value)
                            else:
                                try:
                                    #print("Yahooooo")
                                    #Gets the previous Q&A if it exists
                                    #current_row = 0
                                    #clockz = -1
                                    jump_qa = ''
                                    #with open('DESPurple' + Datee + '.csv', 'r') as f:
                                        #reader = csv.reader(f, delimiter="\t")
                                        #for k, line in enumerate(reader):
                                            #current_row = k
                                            #print('line[{}] = {}'.format(k,line))
                                    #f.close()
                                    with open('DESPurple' + Datee + '.csv', 'r') as f:
                                        readingz = csv.DictReader(f, delimiter=",")
                                        rowz = list(readingz)
                                        current_index = jsonObject1.get('sensor_index')
                                        for row in reversed(rowz):
                                            #clockz = clockz + 1
                                            #if(clockz == (current_row - amount)):
                                                #jump_qa = row['Q&A']
                                            if(str(current_index) == row['sensor_index']):
                                                print(row['sensor_index'])
                                                jump_qa = row['Q&A']
                                                print(row['Q&A'])
                                                break
                                    f.close()
                                    diff_index = arrayKeys.index("Diff")
                                    rd_index = arrayKeys.index("Rel Dif")
                                    diff = arrayValues[diff_index]
                                    rd = arrayValues[sd_index]
                                    print("Hey I'm here")
                                    #humidity = arrayValues[10]
                                    #print(humidity)
                                    if(jump_qa == 'JA' and float(jump_b) < float(Diff_threshold) and float(rd) > float(rd_threshold)):
                                        value = 'JA'
                                        guard = True
                                        arrayValues.append(value)
                                    elif(jump_qa == 'JB' and float(jump_a) < float(Diff_threshold) and float(rd) > float(rd_threshold)):
                                        value = 'JB'
                                        guard = True
                                        arrayValues.append(value)  
                                    #New Logic 07_27_2022
                                    elif(jump_qa == 'JARH' and float(jump_b) < float(Diff_threshold) and float(rd) > float(rd_threshold)):
                                        if(humidity == "None"):
                                            value = 'JARH'
                                            guard = True
                                            arrayValues.append(value)
                                        else:
                                            value = 'JA'
                                            guard = True
                                            arrayValues.append(value)
                                    elif(jump_qa == 'JARH' and humidity == "None"):
                                            value = 'RH'
                                            guard = True
                                            arrayValues.append(value)
                                    elif(jump_qa == 'JBRH' and float(jump_a) < float(Diff_threshold) and float(rd) > float(rd_threshold)):
                                        if(humidity == "None"):
                                            value = 'JBRH'
                                            guard = True
                                            arrayValues.append(value)
                                        else:
                                            value = 'JB'
                                            guard = True
                                            arrayValues.append(value)
                                    elif(jump_qa == 'JBRH' and humidity == "None"):
                                            value = 'RH'
                                            guard = True
                                            arrayValues.append(value)
                                    #End of new logic
                                    elif(float(diff) > float(Diff_threshold) and float(rd) > float(rd_threshold)):
                                        value = 'QQ'
                                        guard = True
                                        arrayValues.append(value)
                                    elif(humidity == "None"):
                                        print('Yo')
                                        value = 'RH'
                                        guard = True
                                        arrayValues.append(value)                                      
                                    elif(guard == False):
                                        temporary = 'Passed'
                                        arrayValues.append(temporary)
                                except:
                                    logging.info("Means there was no previous Q&A yet")
                                    temporary = 'Passed'
                                    arrayValues.append(temporary)
                                    pass
                        elif(i == "Uncorrected Average"):
                            a_index = arrayKeys.index("A")
                            b_index = arrayKeys.index("B")
                            qa_index = arrayKeys.index("Q&A")
                            a = arrayValues[a_index]
                            b = arrayValues[b_index]
                            qa = arrayValues[qa_index]
                            #Needs Max otherwise in here
                            if(qa == "JB" or qa == "JBRH"):
                                temporary = a
                                arrayValues.append(a)
                            elif(qa == "JA" or qa == "JARH"):
                                temporary = b
                                arrayValues.append(b)
                            elif(qa == "Passed" or qa == "RH"):
                                average = ((float(a) + float(b)) / 2)
                                average = round(average, 2)
                                arrayValues.append(average)
                            elif(qa == "QQ"):
                                temporary = 'None'
                                arrayValues.append(temporary)
                        elif(i == "Corrected Value"):
                            qa_index = arrayKeys.index("Q&A")
                            uncorrect_index = arrayKeys.index("Uncorrected Average")
                            uncorrect = arrayValues[uncorrect_index]
                            humidity_index = arrayKeys.index("humidity")
                            qa = arrayValues[qa_index]
                            humidity = arrayValues[humidity_index]
                            lat_index = arrayKeys.index("latitude")
                            long_index = arrayKeys.index("longitude")
                            if(uncorrect == 'None'):
                                temporary = 'None'
                                value = 'Fix'
                                arrayValues.append(temporary)
                                mapCSV(jsonObject1, value)
                            elif(qa == "JBRH" or qa == "JARH" or qa == "RH"):
                                #print(arrayValues[3])
                                #print(arrayValues[4])
                                humidity1 = airportData(float(arrayValues[lat_index]), float(arrayValues[long_index]))
                                final_value = round((((0.61 * float(uncorrect)) - (0.07 * float(humidity1))) + 2.16),2)
                                arrayValues.append(final_value)
                                mapCSV(jsonObject1, final_value)
                            else:
                                final_value = round((((0.61 * float(uncorrect)) - (0.07 * float(humidity))) + 2.16),2)
                                arrayValues.append(final_value)
                                mapCSV(jsonObject1, final_value)
                        else:
                            temporary = 'None'
                            #We then add this string value to our array of values
                            arrayValues.append(temporary)
                    except:
                        pass
                        logging.info('If you get this message, your keyword of ' + i + ' does not exist in the json file.')
                    
                #Once the for loop is complete, all of our values are ready to write in the .csv so we do so with our writer object
                csvcurrent.writerow(arrayValues)
                #Now we close the .csv file since we have written all the values inside 
                csvcurrentfile.close()
            except:
                #We log when an error occurs which I'm predicting to be a simple wrong dictionary error in most cases
                logging.error('Problem with finding the correct dictionary/key in a subsection of the JSON')
                logging.info('Examine the Json file for certain keywords you want and figure out which jsonObject holds the key(s) you want to grab')
                #We log the time of the program exit to signal the error time and that the program had errored out
                logging.info('Time of program exit ' + datetime.now().strftime('%m/%d/%Y %H:%M:%S'))
        #A conditional else if statement asks if bool is true which means that we'll need to append to the already existing .Csv file
        elif bool == True:
            #These arrays hold the Key's and the ready to be filled values we'll pull from the dicitionary objects
            #arrayKeys = ["data_time_stamp","humidity","sensor_index", "name", "pm1.0", "pm1.0_a", "pm1.0_b","pm2.5", "pm2.5_a", "pm2.5_b", "pm10.0", "pm10.0_a", "pm10.0_b"]
            arrayValues = []
            #Print hey show's we're working; I'll need to take it out later *NOTED*
            #print("Hey")
            #Try and except as a saftey net to keep the code from breaking in error moments
            try:
                index = -1
                dict_1 = False;
                dict_2 = False;
                dict_3 = False;
                dict_4 = False;
                dict_5 = False;
                #For loop goes through arrayKeys and i is each value being iterated through
                for i in arrayKeys:
                    index = index + 1
                    '''
                        #This conditional if looks for the "data_time_stamp" that is special because it needs to be converted from epoch
                        if(i == "data_time_stamp" or i == "time_stamp"):
                            #We assign the value of temporary to the epoch value found when given the key through our json dicitionary object
                            temporary = jsonObject.get(i)
                            #We set the string value of d equal to the string of the datetime converting our temporary and formatting it with strftime to fit our needs
                            d = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S')) 
                            #We now put that into our array of values
                            arrayValues.append(d)
                        #Else will include everything else because they require zero conversions
                        else:
                    '''
                    #print("i is: " + i)
                    #print(dict_1)
                    #print(dict_2)
                    #print(dict_3)
                    #print(dict_4)
                    #print(dict_5)
                    clock = 0
                    try:
                        if((i in keyIndex) == True):
                            temps = helpme(jsonObject, jsonObject1, jsonObject2, jsonObject3, jsonObject4, i, keyIndex, duplicateSpecify)
                            #print(temps)
                            arrayValues.append(temps)
                            #print(arrayValues)
                            clock = 1
                            continue
                    except:
                        pass
                    try:
                        if(clock != 1 and str(jsonObject.get(i)) != 'None' and dict_1 == False):
                            if(i == "time_stamp"):
                                #We assign the value of temporary to the epoch value found when given the key through our json dicitionary object
                                temporary = jsonObject.get(i)
                                #We set the string value of d equal to the string of the datetime converting our temporary and formatting it with strftime to fit our needs
                                d = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S')) 
                                #We now put that into our array of values
                                arrayValues.append(d)
                                continue
                            elif(i == "data_time_stamp"):
                                #We assign the value of temporary to the epoch value found when given the key through our json dicitionary object
                                temporary = jsonObject.get(i)
                                #We set the string value of d equal to the string of the datetime converting our temporary and formatting it with strftime to fit our needs
                                d = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S')) 
                                #We now put that into our array of values
                                arrayValues.append(d)
                                dict_1 = True
                                clock = 1
                                continue
                            else:
                                #We assign the value found by giving our key into the dicitionary object and convert it to a string
                                #print(i)
                                temporary = str(jsonObject.get(i))
                                #We then add this string value to our array of values
                                arrayValues.append(temporary)
                                clock = 1
                                continue
                    except:
                        pass
                    try: 
                        if(clock != 1 and str(jsonObject1.get(i)) != 'None' and dict_2 == False):
                            if(i == "last_modified" or i == "date_created" or i == "last_seen"):
                                #We assign the value of temporary to the epoch value found when given the key through our json dicitionary object
                                temporary = jsonObject1.get(i)
                                #We set the string value of d equal to the string of the datetime converting our temporary and formatting it with strftime to fit our needs
                                d = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S')) 
                                #We now put that into our array of values
                                arrayValues.append(d)
                                continue
                            elif(i == "secondary_key_b"):
                                #We assign the value found by giving our key into the dicitionary object and convert it to a string
                                #print(i)
                                temporary = str(jsonObject1.get(i))
                                #We then add this string value to our array of values
                                arrayValues.append(temporary)
                                clock = 1
                                dict_2 = True
                                continue
                            else:
                                #We assign the value found by giving our key into the dicitionary object and convert it to a string
                                #print(i)
                                temporary = str(jsonObject1.get(i))
                                #We then add this string value to our array of values
                                arrayValues.append(temporary)
                                clock = 1
                                continue
                    except:
                        pass
                    try:
                        if(clock != 1 and str(jsonObject2.get(i)) != 'None' and dict_3 == False):
                            if(i == "time_stamp"):
                                #We assign the value of temporary to the epoch value found when given the key through our json dicitionary object
                                temporary = jsonObject2.get(i)
                                #We set the string value of d equal to the string of the datetime converting our temporary and formatting it with strftime to fit our needs
                                d = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S')) 
                                #We now put that into our array of values
                                arrayValues.append(d)
                                dict_3 = True
                                clock = 1
                                continue
                            else:
                                #We assign the value found by giving our key into the dicitionary object and convert it to a string
                                #print(i)
                                temporary = str(jsonObject2.get(i))
                                #We then add this string value to our array of values
                                arrayValues.append(temporary)
                                clock = 1
                                continue
                    except:
                        pass
                    try:
                        if(clock != 1 and str(jsonObject3.get(i)) != 'None' and dict_4 == False):
                            if(i == "time_stamp"):
                                #We assign the value of temporary to the epoch value found when given the key through our json dicitionary object
                                temporary = jsonObject3.get(i)
                                #We set the string value of d equal to the string of the datetime converting our temporary and formatting it with strftime to fit our needs
                                d = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S')) 
                                #We now put that into our array of values
                                arrayValues.append(d)
                                dict_4 = True
                                clock = 1
                                continue
                            else:
                                #We assign the value found by giving our key into the dicitionary object and convert it to a string
                                #print(i)
                                temporary = str(jsonObject3.get(i))
                                #We then add this string value to our array of values
                                arrayValues.append(temporary)
                                clock = 1
                                continue
                    except:
                        pass
                    try:
                        if(clock != 1 and str(jsonObject4.get(i)) != 'None' and dict_5 == False):
                            if(i == "time_stamp"):
                                #We assign the value of temporary to the epoch value found when given the key through our json dicitionary object
                                temporary = jsonObject4.get(i)
                                #We set the string value of d equal to the string of the datetime converting our temporary and formatting it with strftime to fit our needs
                                d = str(datetime.fromtimestamp(temporary).strftime('%m-%d-%Y %H:%M:%S')) 
                                #We now put that into our array of values
                                arrayValues.append(d)
                                dict_5 = True
                                clock = 1
                                continue
                            else:
                                #We assign the value found by giving our key into the dicitionary object and convert it to a string
                                #print(i)
                                temporary = str(jsonObject4.get(i))
                                #We then add this string value to our array of values
                                arrayValues.append(temporary)
                                clock = 1
                                continue
                        elif(i == "stats" or i == "stats_a" or i == "stats_b" or i == "sensor" or i == "channel a" or i == "channel b"):
                            temporary = ''
                            arrayValues.append(temporary)
                        elif(i == "Location"):
                            temp_long = jsonObject1.get("longitude")
                            #print(temp_long)
                            temp_lat = jsonObject1.get("latitude")
                            #print(temp_lat)
                            loco = locationz(temp_long, temp_lat)
                            arrayValues.append(loco)
                            #print(loco['city'])
                            clock = 1
                        #Channel A 10 minute average
                        elif(i == "A"):
                            temporary = jsonObject3.get("pm2.5_10minute")
                            arrayValues.append(temporary)
                        #Channel B 10 minute average
                        elif(i == "B"):
                            temporary = jsonObject4.get("pm2.5_10minute")
                            arrayValues.append(temporary)
                        #Difference between channel A and B
                        elif(i == "Diff"):
                            temporary_a = jsonObject3.get("pm2.5_10minute")
                            temporary_b = jsonObject4.get("pm2.5_10minute")
                            value = abs(temporary_a - temporary_b)
                            value = round(value, 2)
                            arrayValues.append(value)
                        #Standard Deviation 
                        elif(i == "Rel Dif"):
                            temporary_a = jsonObject3.get("pm2.5_10minute")
                            temporary_b = jsonObject4.get("pm2.5_10minute")
                            value_mean = float(temporary_a - temporary_b)
                            #value_sum = ((temporary_a - value_mean) ** 2) + ((temporary_b - value_mean) ** 2)
                            value_sum = float((temporary_a + temporary_b) / 2)
                            value_final = float((value_mean / value_sum) * 100) 
                            value_final = round(value_final,0)
                            arrayValues.append(value_final)
                            print(str(value_final))
                        #Logic of JumpA is fixed
                        elif(i =="JumpA"):
                            try:
                                #current_row = 0
                                #clockz = -1
                                #timer = 0
                                num_a = ''
                                jump_a = ''
                                #with open('DESPurple' + Datee + '.csv', 'r') as f:
                                    #reader = csv.reader(f, delimiter="\t")
                                    #for k, line in enumerate(reader):
                                        #current_row = k
                                        #print('line[{}] = {}'.format(k,line))
                                #f.close()
                                with open('DESPurple' + Datee + '.csv', 'r') as f:
                                    readingz = csv.DictReader(f, delimiter=",")
                                    rowz = list(readingz)
                                    #first = 0
                                    current_index = jsonObject1.get('sensor_index')
                                    for row in reversed(rowz):
                                        #if(first == 0):
                                            #current_index = row['sensor_index']
                                        #clockz = clockz + 1
                                        #if(clockz == (current_row - amount)):
                                        if(str(current_index) == row['sensor_index']):
                                            print(row['sensor_index'])
                                            jump_a = row['A']
                                            print(row['A'])
                                            break
                                            #arrayValues.append(row['A'])
                                        #first = 1 
                                    '''
                                    for rowing in rowz:
                                        print("Thing " + str(current_row - timer))
                                        timer = timer + 1                                    
                                        if(0 == (current_row - timer)):
                                            num_a = rowing['A']
                                            print(rowing['A'])
                                    '''
                                    num_a = jsonObject3.get("pm2.5_10minute")
                                    print("First number: " + str(num_a))
                                    print("Second number: " + jump_a)
                                    ending = abs(float(jump_a) - float(num_a))
                                    ending = round(ending, 2)
                                    print("End value: " + str(ending))
                                    arrayValues.append(str(ending))
                                    #print(arrayValues)
                                f.close()
                                #print("This row is: " + str(current_row))
                            except:
                                logging.info("Must be the first iteration for the day!")
                                arrayValues.append(0)
                                #print(amount)
                        elif(i =="JumpB"):
                            try:
                                #current_row = 0
                                #clockz = -1
                                jump_b = ''
                                num_b = ''
                                #with open('DESPurple' + Datee + '.csv', 'r') as f:
                                    #reader = csv.reader(f, delimiter="\t")
                                    #for k, line in enumerate(reader):
                                        #current_row = k
                                        #print('line[{}] = {}'.format(k,line))
                                #f.close()
                                with open('DESPurple' + Datee + '.csv', 'r') as f:
                                    readingz = csv.DictReader(f, delimiter=",")
                                    rowz = list(readingz)
                                    current_index = jsonObject1.get('sensor_index')
                                    for row in reversed(rowz):
                                        #clockz = clockz + 1
                                        #if(clockz == (current_row - amount)):
                                            #jump_b = row['B']
                                            #arrayValues.append(row['B'])
                                        if(str(current_index) == row['sensor_index']):
                                            print(row['sensor_index'])
                                            jump_b = row['B']
                                            print(row['B'])
                                            break
                                    num_b = jsonObject4.get("pm2.5_10minute")
                                    print("2First number: " + str(num_b))
                                    print("2Second number: " + jump_b)
                                    ending = abs(float(jump_b) - float(num_b))
                                    ending = round(ending, 2)
                                    print("2End value: " + str(ending))
                                    arrayValues.append(str(ending))
                                    #print(arrayValues)
                                #f.close()
                                #print("This row is: " + str(current_row))
                                #print(amount)
                                f.close()
                                #print("This row is: " + str(current_row))
                            except:
                                logging.info("Must be the first iteration for the day!")
                                arrayValues.append(0)
                        elif(i =="Rel Dif"):
                            #print(str(arrayKeys.index("JumpA")))
                            #print(str(arrayKeys.index("JumpB")))
                            jump_a_index = arrayKeys.index("JumpA")
                            jump_b_index = arrayKeys.index("JumpB")
                            temporary_a = float(arrayValues[jump_a_index])
                            temporary_b = float(arrayValues[jump_b_index])
                            #print(str(temporary_a))
                            #print(str(temporary_b))
                            value_mean = ((temporary_a + temporary_b) / 2)
                            value_sum = ((temporary_a - value_mean) ** 2) + ((temporary_b - value_mean) ** 2)
                            #print("hey there")
                            value_final = float(sqrt((1/2) * value_sum))
                            arrayValues.append(value_final)
                        elif(i =="Q&A"):
                            #variables for tests
                            RD_threshold = 125
                            #EPA one
                            rd_threshold = 50
                            A_threshold = 7
                            B_threshold = 7
                            Diff_threshold = 10
                            #Four Tests
                            jump_a_index = arrayKeys.index("JumpA")
                            jump_b_index = arrayKeys.index("JumpB")
                            jump_sd_index = arrayKeys.index("Rel Dif")
                            humidity_index = arrayKeys.index("humidity")
                            jump_a = arrayValues[jump_a_index]
                            print("jumpa " + str(jump_a))
                            jump_b = arrayValues[jump_b_index]
                            print(arrayKeys)
                            jump_sd = arrayValues[jump_sd_index]
                            humidity = arrayValues[humidity_index]
                            value = ''
                            guard = False
                            #Test 1
                            #Initiates when Jump_a is bigger than the threshold
                            #print(jump_sd)
                            #print("Yahooooo")
                            if(float(jump_sd) > float(SD_threshold) and float(jump_a) > float(A_threshold) and float(jump_b) <= float(B_threshold)):
                                #print("Yehaw")
                                if(humidity == "None"):
                                    value = "JARH"
                                    guard = True
                                    arrayValues.append(value)
                                else:
                                    value = 'JA'
                                    guard = True
                                    arrayValues.append(value)
                            #Initiates when Jump_b is bigger than the threshold
                            elif(float(jump_sd) > float(SD_threshold) and float(jump_a) <= float(A_threshold) and float(jump_b) > float(B_threshold)):
                                #print("horse")
                                if(humidity == "None"):
                                    value = "JBRH"
                                    guard = True
                                    arrayValues.append(value)  
                                else:
                                    value = 'JB'
                                    guard = True
                                    arrayValues.append(value)
                            else:
                                try:
                                    #print("Yahooooo")
                                    #Gets the previous Q&A if it exists
                                    #current_row = 0
                                    #clockz = -1
                                    jump_qa = ''
                                    #with open('DESPurple' + Datee + '.csv', 'r') as f:
                                        #reader = csv.reader(f, delimiter="\t")
                                        #for k, line in enumerate(reader):
                                            #current_row = k
                                            #print('line[{}] = {}'.format(k,line))
                                    #f.close()
                                    with open('DESPurple' + Datee + '.csv', 'r') as f:
                                        readingz = csv.DictReader(f, delimiter=",")
                                        rowz = list(readingz)
                                        current_index = jsonObject1.get('sensor_index')
                                        for row in reversed(rowz):
                                            #clockz = clockz + 1
                                            #if(clockz == (current_row - amount)):
                                                #jump_qa = row['Q&A']
                                            if(str(current_index) == row['sensor_index']):
                                                print(row['sensor_index'])
                                                jump_qa = row['Q&A']
                                                print(row['Q&A'])
                                                break
                                    f.close()
                                    diff_index = arrayKeys.index("Diff")
                                    rd_index = arrayKeys.index("Rel Dif")
                                    diff = arrayValues[diff_index]
                                    rd = arrayValues[rd_index]
                                    print("Hey I'm here")
                                    #humidity = arrayValues[10]
                                    #print(humidity)
                                    if(jump_qa == 'JA' and float(jump_b) < float(Diff_threshold) and float(rd) > float(rd_threshold)):
                                        value = 'JA'
                                        guard = True
                                        arrayValues.append(value)
                                    elif(jump_qa == 'JB' and float(jump_a) < float(Diff_threshold) and float(rd) > float(rd_threshold)):
                                        value = 'JB'
                                        guard = True
                                        arrayValues.append(value)  
                                    #New Logic 07_27_2022
                                    elif(jump_qa == 'JARH' and float(jump_b) < float(Diff_threshold) and float(rd) > float(rd_threshold)):
                                        if(humidity == "None"):
                                            value = 'JARH'
                                            guard = True
                                            arrayValues.append(value)
                                        else:
                                            value = 'JA'
                                            guard = True
                                            arrayValues.append(value)
                                    elif(jump_qa == 'JARH' and humidity == "None"):
                                            value = 'RH'
                                            guard = True
                                            arrayValues.append(value)
                                    elif(jump_qa == 'JBRH' and float(jump_a) < float(Diff_threshold) and float(rd) > float(rd_threshold)):
                                        if(humidity == "None"):
                                            value = 'JBRH'
                                            guard = True
                                            arrayValues.append(value)
                                        else:
                                            value = 'JB'
                                            guard = True
                                            arrayValues.append(value)
                                    elif(jump_qa == 'JBRH' and humidity == "None"):
                                            value = 'RH'
                                            guard = True
                                            arrayValues.append(value)
                                    #End of new logic
                                    elif(float(diff) > float(Diff_threshold) and float(rd) > float(rd_threshold)):
                                        value = 'QQ'
                                        guard = True
                                        arrayValues.append(value)
                                    elif(humidity == "None"):
                                        print('Yo')
                                        value = 'RH'
                                        guard = True
                                        arrayValues.append(value)                                      
                                    elif(guard == False):
                                        temporary = 'Passed'
                                        arrayValues.append(temporary)
                                except:
                                    logging.info("Means there was no previous Q&A yet")
                                    temporary = 'Passed'
                                    arrayValues.append(temporary)
                                    pass
                        elif(i == "Uncorrected Average"):
                            a_index = arrayKeys.index("A")
                            b_index = arrayKeys.index("B")
                            qa_index = arrayKeys.index("Q&A")
                            a = arrayValues[a_index]
                            b = arrayValues[b_index]
                            qa = arrayValues[qa_index]
                            #Needs Max otherwise in here
                            if(qa == "JB" or qa == "JBRH"):
                                temporary = a
                                arrayValues.append(a)
                            elif(qa == "JA" or qa == "JARH"):
                                temporary = b
                                arrayValues.append(b)
                            elif(qa == "Passed" or qa == "RH"):
                                average = ((float(a) + float(b)) / 2)
                                average = round(average, 2)
                                arrayValues.append(average)
                            elif(qa == "QQ"):
                                temporary = 'None'
                                arrayValues.append(temporary)
                        elif(i == "Corrected Value"):
                            qa_index = arrayKeys.index("Q&A")
                            uncorrect_index = arrayKeys.index("Uncorrected Average")
                            uncorrect = arrayValues[uncorrect_index]
                            humidity_index = arrayKeys.index("humidity")
                            qa = arrayValues[qa_index]
                            humidity = arrayValues[humidity_index]
                            lat_index = arrayKeys.index("latitude")
                            long_index = arrayKeys.index("longitude")
                            if(uncorrect == 'None'):
                                temporary = 'None'
                                value = 'Fix'
                                arrayValues.append(temporary)
                                mapCSV(jsonObject1, value)
                            elif(qa == "JBRH" or qa == "JARH" or qa == "RH"):
                                #print(arrayValues[3])
                                #print(arrayValues[4])
                                humidity1 = airportData(float(arrayValues[lat_index]), float(arrayValues[long_index]))
                                final_value = round((((0.61 * float(uncorrect)) - (0.07 * float(humidity1))) + 2.16),2)
                                arrayValues.append(final_value)
                                mapCSV(jsonObject1, final_value)
                            else:
                                final_value = round((((0.61 * float(uncorrect)) - (0.07 * float(humidity))) + 2.16),2)
                                arrayValues.append(final_value)
                                mapCSV(jsonObject1, final_value)
                        else:
                            temporary = 'None'
                            #We then add this string value to our array of values
                            arrayValues.append(temporary)
                    except:
                        pass
                        logging.info('If you get this message, your keyword of ' + i + ' does not exist in the json file.')
                csvcurrentfile = open('DESPurple' + Datee + '.csv', 'a', newline = '')
                csv_writer = writer(csvcurrentfile)
                #Once the for loop is complete, all of our values are ready to write in the .csv so we do so with our writer object
                csv_writer.writerow(arrayValues)
                #Now we close the .csv file since we have written all the values inside 
                #print(arrayValues)
                csvcurrentfile.close()
            except:
                #We log when an error occurs which I'm predicting to be a simple wrong dictionary error in most cases
                logging.error('Problem with finding the correct dictionary/key in a subsection of the JSON')
                logging.info('Examine the Json file for certain keywords you want and figure out which jsonObject holds the key(s) you want to grab')
                #We log the time of the program exit to signal the error time and that the program had errored out
                logging.info('Time of program exit ' + datetime.now().strftime('%m/%d/%Y %H:%M:%S'))
    except:
        #Log whenever this method error's out and if it does it's not because of an anticipated error I could foresee
        logging.error('Unexpected Error')
        #We log the time of the program exit to signal the error time and that the program had errored out
        logging.info('Time of program exit ' + datetime.now().strftime('%m/%d/%Y %H:%M:%S'))    
'''        
Main driver function
This function of Jsonmyhero() just calls both main helper methods of readIni and API that do the heavy lifting
'''
def Jsonmyhero():
    #Try and except as a saftey net to keep the code from breaking in error moments
    try: 
        #We call the helper method of readIni() to do it's part of creating/reading the .ini file
        readIni()
    except:
        #We log any errors which means that it happened inside of the helper method of readIni()
        logging.error('Error occured inside of readIni() method')
        #We log the time of the program exit to signal the error time and that the program had errored out
        logging.info('Time of program exit ' + datetime.now().strftime('%m/%d/%Y %H:%M:%S'))
    #Try and except as a saftey net to keep the code from breaking in error moments        
    try:
        #We call the helper method of API() to do it's part contacting the API server, getting the json, creating the dictionaries from the json, seeing if the .csv exists, and finally populating/creating our .csv file
        API()
        #airportData()
        #mapMaking()
    except:
        #We log any errors which means that it happened inside of the helper method of API()
        logging.error('Error occured inside of API() method')
        #We log the time of the program exit to signal the error time and that the program had errored out
        logging.info('Time of program exit ' + datetime.now().strftime('%m/%d/%Y %H:%M:%S'))
#Main function for our program
def main():
    #Call to the main drive function
    Jsonmyhero()
    mapMaking()
    #We log the completetion time of our program; which if it hit this point we had no errors!
    logging.info('Time of program completion ' + datetime.now().strftime('%m/%d/%Y %H:%M:%S'))
    #This kills the logging and shuts the file so it can give the move method permission to move it
    logging.shutdown()
    #logging.close()
#Call to main function
main()
#This moves our log files to the log folder
shutil.move(fileLocation,desinationLocation)