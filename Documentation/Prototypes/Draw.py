import csv, json, datetime, urllib.request, configparser, logging
from datetime import datetime, date, timezone
from csv import writer
global currentDate
currentDate = date.today()
Datee = currentDate.strftime("%m%d%Y")
def readIni():
    global api, units
    defaults = {
    'api':  'True',
    'units': '',    
    }
    config = configparser.ConfigParser(defaults,allow_no_value=True)
    config.add_section('Main')
    try:
        f = open ("Demo.ini", 'r')
        config.read_file(f)
        f.close()
    except:
        pass
    f = open ("Demo.ini", 'w')
    config.write(f)
    items = {x[0]:x[1] for x in config.items('Main')}
    api         = items['api'] == 'True'
    units       = str(items['units']) 
def API():
    for unit in units.split('|'):
        out = open ("DemoAPI.json","w")
        print("Unit is " + unit)
        url = "https://api.purpleair.com/v1/sensors/%s"\
                "?api_key=1F29022F-5079-11EB-9893-42010A8001E8" % (unit)
        f = urllib.request.urlopen (url)
        buff = f.read(); f.close()
        j = json.loads(buff)
        json.dump(j, out, indent = 2)
        out.close() 
        k = open('DemoAPI.json')
        collection = json.load(k)
        strdata = str(collection)
        jsonData1 = collection["sensor"]
        jsonData2 = jsonData1["stats"]
        jsonData3 = jsonData1["stats_a"]
        jsonData4 = jsonData1["stats_b"]
        k.close()
        exists = checkToC()
        print(str(exists))
        createCSV(collection, jsonData1, jsonData2, jsonData3, jsonData4, exists)
  
def checkToC():
    try:
        csvcurrentfile = open('DESPurple' + Datee + '.csv', 'r')
        exists = True
        return exists
    except:
        exists = False
        return exists
   
def createCSV(jsonObject, jsonObject1, jsonObject2, jsonObject3, jsonObject4, bool):
    try:
        if bool == False:
            arrayKeys = ["data_time_stamp","humidity","sensor_index", "name", "pm1.0", "pm1.0_a", "pm1.0_b","pm2.5", "pm2.5_a", "pm2.5_b", "pm10.0", "pm10.0_a", "pm10.0_b"]
            arrayValues = []
            csvcurrentfile = open('DESPurple' + Datee + '.csv', 'w', newline = '')
            print("Hey")
            csvcurrent = csv.writer(csvcurrentfile)
            csvcurrent.writerow(arrayKeys)
            for i in arrayKeys:
                if(i == "data_time_stamp"):
                    temporary = jsonObject.get(i)
                    d = str(datetime.fromtimestamp(temporary).strftime('%d-%m-%Y %H:%M:%S')) 
                    arrayValues.append(d)
                else:
                    temporary = str(jsonObject1.get(i))
                    arrayValues.append(temporary)
            csvcurrent.writerow(arrayValues)
            csvcurrentfile.close()
        elif bool == True:
            arrayKeys = ["data_time_stamp","humidity","sensor_index", "name", "pm1.0", "pm1.0_a", "pm1.0_b","pm2.5", "pm2.5_a", "pm2.5_b", "pm10.0", "pm10.0_a", "pm10.0_b"]
            arrayValues = []
            for i in arrayKeys:
                if(i == "data_time_stamp"):
                    temporary = jsonObject.get(i)
                    d = str(datetime.fromtimestamp(temporary).strftime('%d-%m-%Y %H:%M:%S')) 
                    arrayValues.append(d)
                else:
                    temporary = str(jsonObject1.get(i))
                    arrayValues.append(temporary)
            csvcurrentfile = open('DESPurple' + Datee + '.csv', 'a', newline = '')
            csv_writer = writer(csvcurrentfile)
            csv_writer.writerow(arrayValues)
            csvcurrentfile.close()
    except:
        print("Check the writerow(s)")    
def Jsonmyhero():
    try: 
        readIni()
        API()
    except:
        print("An error has occured")
def main():
	Jsonmyhero()
main()