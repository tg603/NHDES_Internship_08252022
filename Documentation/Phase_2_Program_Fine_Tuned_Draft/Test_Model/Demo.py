import csv, json, datetime
from datetime import datetime
from csv import writer
#Creates a Csv file called Demo.csv
#Global variable for the array
global arrayKeys, arrayValues, statement
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
def readIni():
    global api, units
    defaults = {
    'api':  'True',
    'unit': '',    
    }
    import configparser
    config = configparser.ConfigParser(defaults,allow_no_value=True)
    config.add_section('Main')
    try:
        f = open ("Demo.ini", 'r')
        config.readfp(f)
        f.close()
    except:
        pass
    f = open ("Demo.ini", 'w')
    config.write(f)
    items = {x[0]:x[1] for x in config.items('Main')}
    api         = items['api'] == 'True'
    units       = str(items['units'])
    
def API():
    out = open ("DemoAPI.json","w")
    outtbl =   []
    outbuff =  []
    for unit in unitslist.split('|'):
        url = "https://api.purpleair.com/v1/sensors/%s"\
                "?api_key=1F29022F-5079-11EB-9893-42010A8001E8" % (unit)
        f = urllib.request.urlopen (url)
        buff = f.read(); f.close()
        j = json.loads(buff)
        outbuff.append(j)
        row = j['sensor']
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