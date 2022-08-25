'''
These are the import packages used down inside my code. 
csv - Creates the comma seperated values file for us to put our data from the Json file into for analyizing
json - Is the JavaScript Object Notation file that will hold all the raw data from the PA Servers
datetime - Allows me to get current time stamps and allows me to convert the time stamps on the Json (Epoch time) to our regular localized time
urllib.request - Is a package that allows us to call the API servers that PA have for their monitors to report back to
configparser - Is a package that helps create the .ini file that we can read without hardcoding unit's into this program
The from's just call certain subsections of these packages for me to use for certain things later on inside of the code
'''
import csv, json, datetime, urllib.request, configparser, logging
from datetime import datetime, date, timezone
from csv import writer
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
logging.basicConfig(filename='Log'+ str(datetime.now().strftime('Date%m%d%YTime%H%M %S')) + '.log',filemode = 'w',level=logging.INFO)
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
        logging.info('Starting API() method')
        #For loop that calls each unit individually inside of the .ini file and each unit should be seperated in there by the character '|' Example: units = 143456|151702|1224
        for unit in units.split('|'):
            #Try and except as a saftey net to keep the code from breaking in error moments        
            try:
                #Object of out is assigned to the opening of the Json file 'DemoAPI.json' with the intentions of writing ('w')
                out = open (unit+"API.json","w")
                #We log the current unit being calling  
                logging.info("Unit is " + unit)
                #This url object is assigned to the portal that gives us the Json from any available PurpleAir; *NOTED* inside the api_key=<YOUR OWN KEY> we are currently using Keene States and we'll need our own
                url = "https://api.purpleair.com/v1/sensors/%s"\
                        "?api_key=1F29022F-5079-11EB-9893-42010A8001E8" % (unit)
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
            createCSV(collection, jsonData1, jsonData2, jsonData3, jsonData4, exists)
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
'''
The method of createCSV() takes in the four json dictionaries that we've pulled inside of the API()
and the boolean that tells us whether we need to create a new .csv or append to the one already in existance.
This method pulls the information needed given from the hardcoded arrays and grabs those keys from the dictionary
objects that it corresponds/lands inside of. 
'''  
def createCSV(jsonObject, jsonObject1, jsonObject2, jsonObject3, jsonObject4, bool):
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
        print(str(keyIndex))
        print(str(duplicateSpecify))
        #We log that we're starting the method of createCSV()
        logging.info('Starting the createCSV() method')
        #A conditional if statement asks if bool is false which means that we'll need to create a brand new .csv file today with the correct header
        if bool == False:
            #These arrays hold the Key's and the ready to be filled values we'll pull from the dicitionary objects
            #arrayKeys = ["data_time_stamp","humidity","sensor_index", "name", "pm1.0", "pm1.0_a", "pm1.0_b","pm2.5", "pm2.5_a", "pm2.5_b", "pm10.0", "pm10.0_a", "pm10.0_b"]
            arrayValues = []
            #Here we open the .csv file and use the write mode of ('w') to create a brand new file
            csvcurrentfile = open('DESPurple' + Datee + '.csv', 'w', newline = '')
            #Print hey show's we're working; I'll need to take it out later *NOTED*
            print("Hey")
            #Here we call the csv.writer and use it on the open portal and assign it to the object of csvcurrent
            csvcurrent = csv.writer(csvcurrentfile)
            #We can use this writer object of csvcurrent to write the header which is just all the values inside of the arrayKeys array
            csvcurrent.writerow(arrayKeys)
            #Try and except as a saftey net to keep the code from breaking in error moments
            try:
                index = -1
                #For loop goes through arrayKeys and i is each value being iterated through
                for i in arrayKeys:
                    index = index + 1
                    clock = 0
                    if((i in keyIndex) == True):
                        spot = keyIndex.index(i)
                        number = str(duplicateSpecify[spot])
                        keyIndex[spot] = ''
                        if(number == '1'):
                            temporary = str(jsonObject1.get(i))
                            arrayValues.append(temporary)
                        elif(number == '2'):
                            temporary = str(jsonObject2.get(i))
                            arrayValues.append(temporary)
                        elif(number == '3'):
                            temporary = str(jsonObject3.get(i))
                            arrayValues.append(temporary)
                        elif(number == '4'):
                            temporary = str(jsonObject4.get(i))
                            arrayValues.append(temporary)
                    else:
                        #This conditional if looks for the "data_time_stamp" that is special because it needs to be converted from epoch
                        if(i == "data_time_stamp" or i == "time_stamp"):
                            #We assign the value of temporary to the epoch value found when given the key through our json dicitionary object
                            temporary = jsonObject.get(i)
                            #We set the string value of d equal to the string of the datetime converting our temporary and formatting it with strftime to fit our needs
                            d = str(datetime.fromtimestamp(temporary).strftime('%d-%m-%Y %H:%M:%S')) 
                            #We now put that into our array of values
                            arrayValues.append(d)
                        #Else will include everything else because they require zero conversions
                        else:
                            try: 
                                if(clock != 1 and str(jsonObject1.get(i)) != 'None'):
                                    if(i == "last_modified" or i == "date_created" or i == "last_seen"):
                                        #We assign the value of temporary to the epoch value found when given the key through our json dicitionary object
                                        temporary = jsonObject1.get(i)
                                        #We set the string value of d equal to the string of the datetime converting our temporary and formatting it with strftime to fit our needs
                                        d = str(datetime.fromtimestamp(temporary).strftime('%d-%m-%Y %H:%M:%S')) 
                                        #We now put that into our array of values
                                        arrayValues.append(d)
                                        continue
                                    else:
                                        #We assign the value found by giving our key into the dicitionary object and convert it to a string
                                        print(i)
                                        temporary = str(jsonObject1.get(i))
                                        #We then add this string value to our array of values
                                        arrayValues.append(temporary)
                                        clock = 1
                                        continue
                            except:
                                pass
                            try:
                                if(clock != 1 and str(jsonObject2.get(i)) != 'None'):
                                    if(i == "data_time_stamp" or i == "time_stamp"):
                                        #We assign the value of temporary to the epoch value found when given the key through our json dicitionary object
                                        temporary = jsonObject2.get(i)
                                        #We set the string value of d equal to the string of the datetime converting our temporary and formatting it with strftime to fit our needs
                                        d = str(datetime.fromtimestamp(temporary).strftime('%d-%m-%Y %H:%M:%S')) 
                                        #We now put that into our array of values
                                        arrayValues.append(d)
                                        continue
                                    else:
                                        #We assign the value found by giving our key into the dicitionary object and convert it to a string
                                        print(i)
                                        temporary = str(jsonObject2.get(i))
                                        #We then add this string value to our array of values
                                        arrayValues.append(temporary)
                                        clock = 1
                                        continue
                            except:
                                pass
                            try:
                                if(clock != 1 and str(jsonObject3.get(i)) != 'None'):
                                    if(i == "data_time_stamp" or i == "time_stamp"):
                                        #We assign the value of temporary to the epoch value found when given the key through our json dicitionary object
                                        temporary = jsonObject3.get(i)
                                        #We set the string value of d equal to the string of the datetime converting our temporary and formatting it with strftime to fit our needs
                                        d = str(datetime.fromtimestamp(temporary).strftime('%d-%m-%Y %H:%M:%S')) 
                                        #We now put that into our array of values
                                        arrayValues.append(d)
                                        continue
                                    else:
                                        #We assign the value found by giving our key into the dicitionary object and convert it to a string
                                        print(i)
                                        temporary = str(jsonObject3.get(i))
                                        #We then add this string value to our array of values
                                        arrayValues.append(temporary)
                                        clock = 1
                                        continue
                            except:
                                pass
                            try:
                                if(clock != 1 and str(jsonObject4.get(i)) != 'None'):
                                    if(i == "data_time_stamp" or i == "time_stamp"):
                                        #We assign the value of temporary to the epoch value found when given the key through our json dicitionary object
                                        temporary = jsonObject4.get(i)
                                        #We set the string value of d equal to the string of the datetime converting our temporary and formatting it with strftime to fit our needs
                                        d = str(datetime.fromtimestamp(temporary).strftime('%d-%m-%Y %H:%M:%S')) 
                                        #We now put that into our array of values
                                        arrayValues.append(d)
                                        continue
                                    else:
                                        #We assign the value found by giving our key into the dicitionary object and convert it to a string
                                        print(i)
                                        temporary = ''
                                        #We then add this string value to our array of values
                                        arrayValues.append(temporary)
                                        clock = 1
                                        continue
                                else:
                                    temporary = str(jsonObject4.get(i))
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
            #Try and except as a saftey net to keep the code from breaking in error moments
            try:
                index = -1
                #For loop goes through arrayKeys and i is each value being iterated through
                for i in arrayKeys:
                    index = index + 1
                    clock = 0
                    if((i in keyIndex) == True):
                        spot = keyIndex.index(i)
                        number = str(duplicateSpecify[spot])
                        keyIndex[spot] = ''
                        if(number == '1'):
                            temporary = str(jsonObject1.get(i))
                            arrayValues.append(temporary)
                        elif(number == '2'):
                            temporary = str(jsonObject2.get(i))
                            arrayValues.append(temporary)
                        elif(number == '3'):
                            temporary = str(jsonObject3.get(i))
                            arrayValues.append(temporary)
                        elif(number == '4'):
                            temporary = str(jsonObject4.get(i))
                            arrayValues.append(temporary)
                    else:
                        #This conditional if looks for the "data_time_stamp" that is special because it needs to be converted from epoch
                        if(i == "data_time_stamp" or i == "time_stamp"):
                            #We assign the value of temporary to the epoch value found when given the key through our json dicitionary object
                            temporary = jsonObject.get(i)
                            #We set the string value of d equal to the string of the datetime converting our temporary and formatting it with strftime to fit our needs
                            d = str(datetime.fromtimestamp(temporary).strftime('%d-%m-%Y %H:%M:%S')) 
                            #We now put that into our array of values
                            arrayValues.append(d)
                        #Else will include everything else because they require zero conversions
                        else:
                            try: 
                                if(clock != 1 and str(jsonObject1.get(i)) != 'None'):
                                    if(i == "last_modified" or i == "date_created" or i == "last_seen"):
                                        #We assign the value of temporary to the epoch value found when given the key through our json dicitionary object
                                        temporary = jsonObject1.get(i)
                                        #We set the string value of d equal to the string of the datetime converting our temporary and formatting it with strftime to fit our needs
                                        d = str(datetime.fromtimestamp(temporary).strftime('%d-%m-%Y %H:%M:%S')) 
                                        #We now put that into our array of values
                                        arrayValues.append(d)
                                        continue
                                    else:
                                        #We assign the value found by giving our key into the dicitionary object and convert it to a string
                                        print(i)
                                        temporary = str(jsonObject1.get(i))
                                        #We then add this string value to our array of values
                                        arrayValues.append(temporary)
                                        clock = 1
                                        continue
                            except:
                                pass
                            try:
                                if(clock != 1 and str(jsonObject2.get(i)) != 'None'):
                                    if(i == "data_time_stamp" or i == "time_stamp"):
                                        #We assign the value of temporary to the epoch value found when given the key through our json dicitionary object
                                        temporary = jsonObject2.get(i)
                                        #We set the string value of d equal to the string of the datetime converting our temporary and formatting it with strftime to fit our needs
                                        d = str(datetime.fromtimestamp(temporary).strftime('%d-%m-%Y %H:%M:%S')) 
                                        #We now put that into our array of values
                                        arrayValues.append(d)
                                        continue
                                    else:
                                        #We assign the value found by giving our key into the dicitionary object and convert it to a string
                                        print(i)
                                        temporary = str(jsonObject2.get(i))
                                        #We then add this string value to our array of values
                                        arrayValues.append(temporary)
                                        clock = 1
                                        continue
                            except:
                                pass
                            try:
                                if(clock != 1 and str(jsonObject3.get(i)) != 'None'):
                                    if(i == "data_time_stamp" or i == "time_stamp"):
                                        #We assign the value of temporary to the epoch value found when given the key through our json dicitionary object
                                        temporary = jsonObject3.get(i)
                                        #We set the string value of d equal to the string of the datetime converting our temporary and formatting it with strftime to fit our needs
                                        d = str(datetime.fromtimestamp(temporary).strftime('%d-%m-%Y %H:%M:%S')) 
                                        #We now put that into our array of values
                                        arrayValues.append(d)
                                        continue
                                    else:
                                        #We assign the value found by giving our key into the dicitionary object and convert it to a string
                                        print(i)
                                        temporary = str(jsonObject3.get(i))
                                        #We then add this string value to our array of values
                                        arrayValues.append(temporary)
                                        clock = 1
                                        continue
                            except:
                                pass
                            try:
                                if(clock != 1 and str(jsonObject4.get(i)) != 'None'):
                                    if(i == "data_time_stamp" or i == "time_stamp"):
                                        #We assign the value of temporary to the epoch value found when given the key through our json dicitionary object
                                        temporary = jsonObject4.get(i)
                                        #We set the string value of d equal to the string of the datetime converting our temporary and formatting it with strftime to fit our needs
                                        d = str(datetime.fromtimestamp(temporary).strftime('%d-%m-%Y %H:%M:%S')) 
                                        #We now put that into our array of values
                                        arrayValues.append(d)
                                        continue
                                    else:
                                        #We assign the value found by giving our key into the dicitionary object and convert it to a string
                                        print(i)
                                        temporary = ''
                                        #We then add this string value to our array of values
                                        arrayValues.append(temporary)
                                        clock = 1
                                        continue
                                else:
                                    temporary = str(jsonObject4.get(i))
                                    #We then add this string value to our array of values
                                    arrayValues.append(temporary)
                            except:
                                pass
                                logging.info('If you get this message, your keyword of ' + i + ' does not exist in the json file.')
                                
                #Here we open the .csv file and use the append mode of ('a') to append to the already created and existing .csv file
                csvcurrentfile = open('DESPurple' + Datee + '.csv', 'a', newline = '')
                csv_writer = writer(csvcurrentfile)
                #All of our values are ready to write in the .csv so we do so with our writer object
                csv_writer.writerow(arrayValues)
                #Now we close the .csv file since we have written all the values inside
                csvcurrentfile.close()
            except:
                #We log when an error occurs which I'm predicting to be a simple wrong dictionary error in most cases
                logging.error('Problem with finding the correct dictionary/key in a subsection of the JSON')
                logging.info('Examine the Json file for certain keywords you want and figure out which jsonObject holds the key(s) you want to grab')
                #We log the time of the program exit to signal the error time and that the program had errored out
                logging.info('Time of program exit ' + datetime.now().strftime('%m/%d/%Y %H:%M:%S'))
        #We log that we're finished with the execution of the createCSV() method
        logging.info('Finished the createCSV() method')
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
    except:
        #We log any errors which means that it happened inside of the helper method of API()
        logging.error('Error occured inside of API() method')
        #We log the time of the program exit to signal the error time and that the program had errored out
        logging.info('Time of program exit ' + datetime.now().strftime('%m/%d/%Y %H:%M:%S'))
#Main function for our program
def main():
    #Call to the main drive function
    Jsonmyhero()
    #We log the completetion time of our program; which if it hit this point we had no errors!
    logging.info('Time of program completion ' + datetime.now().strftime('%m/%d/%Y %H:%M:%S'))
#Call to main function
main()