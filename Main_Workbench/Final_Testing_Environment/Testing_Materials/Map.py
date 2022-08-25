import csv, json
def jsonLateral():
    start = True
    clock = 0
    with open('NH.csv', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            #Loco = "Location" + str(clock)
            Deets = "Details" + str(clock) 
            Data = {
            Deets: {
                "latitude" : row['latitude'],
                "longitude" : row['longitude'],
                "Name" : row['name'],
                "PM2.5" : row['pm2.5']
            }}
            if(start == True):
                start = False
                clock = clock + 1
                with open('data.json', 'w') as file:
                    file.write(json.dumps(Data, ensure_ascii=False, indent = 2))
            else:
                clock = clock + 1
                with open('data.json', 'a') as file:
                    file.write(json.dumps(Data, ensure_ascii=False, indent = 2)) 
        file.close()
    file.close()
    k = open('data.json')
    collection = json.load(k)
    strdata = str(collection)
    print(strdata)
    #jsonData1 = collection["sensor"]
    #jsonData2 = jsonData1["stats"]
    #jsonData3 = jsonData1["stats_a"]
    #jsonData4 = jsonData1["stats_b"]
    k.close()
jsonLateral()