import csv, json, datetime, urllib.request, pandas
from datetime import datetime, date, timezone
from csv import writer
#Creates a Csv file called Demo.csv
#Global variable for the array
global arrayKeys, arrayValues, statement
global currentDate
currentDate = date.today()
Datee = currentDate.strftime("%m%d%Y")
print("Date is " + Datee)
def createCsv(jsonobj, bool):
	try:
		if bool == False:
			arrayKeys = []
			arrayValues = []
			#For loop sorts and puts keys into an Array to reference
			for i in jsonobj.keys():
				arrayKeys.append(i)
			for i in jsonobj.values():
				arrayValues.append(i)
			print("Keys " + str(arrayKeys))
			print("Values " + str(arrayValues))
			#fields = ['ID', 'Longitude', 'Latitude', 'PM']
			#data = [ ['1234', '-70', '68', '2'], ['1232', '-70', '68', '2'], ['234', '-70', '68', '3'], ['421', '-70', '68', '0'], ['1224', '-70', '68', '1']]
			csvcurrentfile = open('Demo.csv', 'w', newline = '')
			csvcurrent = csv.writer(csvcurrentfile)
			csvcurrent.writerow(arrayKeys)
			csvcurrent.writerow(arrayValues)
			csvcurrentfile.close()
		elif bool == True:
			arrayKeys = []
			arrayValues = []
			#For loop sorts and puts keys into an Array to reference
			for i in jsonobj.keys():
				arrayKeys.append(i)
			for i in jsonobj.values():
				arrayValues.append(i)
			print("Keys " + str(arrayKeys))
			print("Values " + str(arrayValues))
			#fields = ['ID', 'Longitude', 'Latitude', 'PM']
			#data = [ ['1234', '-70', '68', '2'], ['1232', '-70', '68', '2'], ['234', '-70', '68', '3'], ['421', '-70', '68', '0'], ['1224', '-70', '68', '1']]
			csvcurrentfile = open('Demo.csv', 'a', newline = '')
			#csvcurrentfile = csv.writer(csvcurrentfile)
			csv_writer = writer(csvcurrentfile)
			#csv_writer.writerow(arrayKeys)
			csv_writer.writerow(arrayValues)
			csvcurrentfile.close()
	except:
		print("Check the writerow(s)")
	'''
		try:
			arrayKeys = []
			arrayValues = []
			#For loop sorts and puts keys into an Array to reference
			for i in jsonobj.keys():
				arrayKeys.append(i)
			for i in jsonobj.values():
				arrayValues.append(i)
			print("Keys " + str(arrayKeys))
			print("Values " + str(arrayValues))
			#fields = ['ID', 'Longitude', 'Latitude', 'PM']
			#data = [ ['1234', '-70', '68', '2'], ['1232', '-70', '68', '2'], ['234', '-70', '68', '3'], ['421', '-70', '68', '0'], ['1224', '-70', '68', '1']]
			csvcurrentfile = open('Demo.csv', 'w', newline = '')
			csvcurrent = csv.writer(csvcurrentfile)
			csvcurrent.writerow(arrayKeys)
			csvcurrent.writerows(arrayValues)
			csvcurrentfile.close()
		except:
	'''
#Helper Method for Jsonmyhero
#Creates a Json file called Demo.json
def createJson():
	today = datetime.now()
	dat = today.strftime("%m/%d/%Y-%H:%M:%S")
	print(dat)
	filename = "Demo.json"
	names = {'Date' : dat, 'ID' : 124, 'Longitude' : -70, 'Latitude' : 68, 'PM' : 4}
	with open(filename, 'w') as f:
		json.dump(names, f, indent=4)
	f.close()
def updateJson():
	today = datetime.now()
	dat = today.strftime("%m/%d/%Y-%H:%M:%S")
	print(dat)
	filename = "Demo.json"
	names = {'Date' : dat, 'ID' : 124, 'Longitude' : -70, 'Latitude' : 68, 'PM' : 4}
	with open(filename, 'w') as f:
		json.dump(names, f, indent=4)
	f.close()
#Helper Method for Jsonmyhero
def readJson():
	try:
		file = open('Demo.json')
		updateJson()
		#takes json file and loads it into a dictionary
		datadict = json.load(file)
		#dictionary is then produced into a string
		stringDict = str(datadict)
		print(stringDict)
		#print("Keys" + datadict.keys())
		'''
		for i in stringDict:
			if i == "'":
				i = i + 1
				print(i)
			else:
				element += i
				print("element is" + element)
			print(i)
		'''
		#return stringDict
		print("Json is already created")
		#Passes the variable to Jsonmyhero()
		statement = True
		return datadict, statement
	except:
		print("Creating json")
		statement = False
		print(bool(statement))
		createJson()
		file = open('Demo.json')
		#takes json file and loads it into a dictionary
		datadict = json.load(file)
		#dictionary is then produced into a string
		stringDict = str(datadict)
		print(stringDict)
		return datadict, statement

'''		
#Helper method for boolean
def whatitis(bool):
	bool = bool
	return bool
	
'''
#Read's/creates an .ini file
def readIni():
    global api, units
    defaults = {
    'api':  'True',
    'units': '',    
    }
    import configparser
    config = configparser.ConfigParser(defaults,allow_no_value=True)
    config.add_section('Main')
    try:
        f = open ("Demo.ini", 'r')
        #print("here")
        config.read_file(f)
        #print("here")
        f.close()
        #print("finished")
    except:
        pass
    f = open ("Demo.ini", 'w')
    config.write(f)
    items = {x[0]:x[1] for x in config.items('Main')}
    api         = items['api'] == 'True'
    units       = str(items['units'])
    #print("finished")
'''
#Phase 2 of API    
def API():
    out = open ("DemoAPI.json","w")
    outbuff =  []
    for unit in units.split(', '):
        try:
            url = https://api.purpleair.com/v1/sensors/:+units.strip()
            f = urllib.request.urlopen (url)
            buff = f.read()
            j = json.loads(buff)
            buff = []
            for line in f:
                line = line.decode("utf-8")
                if ',' in line:
                    buff.append (line)
            f.close()
            json.dump(buff, out)
            #outbuff.append(j)
        except:
            continue
        r = j["results"][0]
        r1 = j["results"][1]
        buff = r["Stats"]
        s = json.loads(buff)
        pm = r['PM2_5Value']
        pm1 = r1['PM2_5Value']
        seen = datetime.datetime.fromtimestamp(r["LastSeen"])
        seen = seen.strftime('%Y_%m_%d_%H%M')
        pressure = temp_f = humidity = 0
        if 'pressure' in r.keys():
            pressure= r['pressure']
        if 'temp_f' in r.keys():
            temp_f= r['temp_f']
        if 'humidity' in r.keys():
            humidity= r['humidity']
    out.write('{"DES":')            # Add a preamable to ensure correct JSON syntax
    json.dump(buff, out)
    #print(unit)
    out.write('}')           #  Close the JSON syntax correctly
    out.close() 
    f.close()
'''
#Beginning start to phase 1 of API method 
#Calls the api server
#loads Json file
#dumps it into our .json file
#Unsticks each subsection to their own Json object
#returns each subsectioned Json Object with each dictionary (keys and values) for writing our .csv   
def API():
    for unit in units.split('|'):
        out = open ("DemoAPI.json","w")
        outtbl =   []
        outbuff =  []
        print("Unit is " + unit)
        url = "https://api.purpleair.com/v1/sensors/%s"\
                "?api_key=1F29022F-5079-11EB-9893-42010A8001E8" % (unit)
        f = urllib.request.urlopen (url)
        buff = f.read(); f.close()
        #print(unit)
        j = json.loads(buff)
        #thing = str(j)
        #print(thing)
        #outbuff.append(j)
        #out.write('{"DES":') 
        json.dump(j, out, indent = 2)
        #out.write('}') 
        '''
        row = j['sensor']
        #print(unit)
        try:
            #print(unit)
            if ( (row['latitude'] >= extentS and row['latitude'] <= extentN) and \
                 (row['longitude'] <= extentE and row['longitude'] >= extentW) ):
                outtbl.append (row)
        except:
            continue 
    #print(unit)
    out.write('{"DES":')            # Add a preamable to ensure correct JSON syntax
    json.dump(outbuff, out, indent = 4)
    #print(unit)
    out.write('}')           #  Close the JSON syntax correctly
    '''
        out.close() 
        #print ("Within the extents Latitude: %9.5f to %9.5f and Logitude %-9.5f to %-9.5f"
        #           % (extentN, extentS, extentE, extentW))
        #print ("The following PurpleAir units were found:")
        #print ("ID     Name            Lat        Lon       Last Seen At    Ver   ChanID  Key")
        #print("Name: " + str(value))
        #print ("\nCut and Paste into Purple.ini:\nunits =  " + msg)
        print(outtbl)
        #Look into now solid data in our JSON file
        k = open('DemoAPI.json')
        collection = json.load(k)
        strdata = str(collection)
        jsonData1 = collection["sensor"]
        jsonData2 = jsonData1["stats"]
        jsonData3 = jsonData1["stats_a"]
        jsonData4 = jsonData1["stats_b"]
        print("Value of stats PM2.5 is " + str(jsonData2.get("pm2.5")))
        print("Value of stats_a PM2.5 is " + str(jsonData3.get("pm2.5")))
        print("Value of stats_b PM2.5 is " + str(jsonData4.get("pm2.5")))
        print(collection.keys())
        print(jsonData1.keys())
        print(jsonData2.keys())
        print(jsonData3.keys())
        print(jsonData4.keys())
        print(collection.keys())
        #print(collection.get("sensor"))
        '''
        #seperate keys and values manually
        clock = 0
        i = 0
        temp = ''
        keys = []
        values = []
        for char_index in range(0, len(strdata)):
            if(strdata[char_index] == "'" and clock == 0):
                clock = 1
                #print("yes")
            elif(strdata[char_index] == "'" and clock == 1):
                #print("yes")
                clock = 0
                print("Temp is " + temp)
                keys += temp
                #print("yes")
                i = i + 1
                temp = ''
            elif(strdata[char_index] != '{' or strdata[char_index] != '}'):
                temp = temp + strdata[char_index]
                print(strdata[char_index])
                '''
        #things = collection.get('api_version')
        #print(str(things))
        #print(str(keys))
        print("hello")
        #print(str(outbuff[0]))
        #k.getJSONObject("sensor").getString("name")
        #name = collection.get("DES")
        #print(str(outbuff))
        #print(str(name))
        k.close()
        #return collection, jsonData1, jsonData2, jsonData3, jsonData4
        #for i in collection:
        #   print(i)
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

#Function for loading, reading, and creating a .csv file from the input
#Main driver function
def Jsonmyhero():
    try: 
        #file = open('Demo.json')
        #dataDict = json.load(file)
        #createJson()
        datadictionary, statement = readJson()
        print(datadictionary.keys())
        #print("Boolean is: " + statement)
        #stringdict = str(datadict)
        createCsv(datadictionary, bool(statement))
        readIni()
        '''
        print("hello")
        m = open('DemoAPI.json')
        collecting = json.load(m)
        print("hello")
        things = collecting.keys()
        print(str(things))
        '''
        #returns the Json four objects (Holds all the keys and corresponding values)
        API()
        '''
        #Keys = str(datadictionary.keys())
        #print("My keys " + Keys)
        arrayKeys = []
        #For loop sorts and puts keys into an Array to reference
        for i in datadictionary.keys():
        arrayKeys.append(i)
        print(str(arrayKeys))
        '''
    except:
        print("An error has occured")
#Main function for our program
def main():
	#print('hi')
	#createCsv()
	#createJson()
	#readJson()
	Jsonmyhero()
	
#Call to main function
main()