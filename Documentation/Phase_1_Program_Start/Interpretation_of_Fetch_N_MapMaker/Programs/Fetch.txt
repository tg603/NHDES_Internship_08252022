import json, urllib.request, time, datetime, pytz
from pprint import pprint as pp
# This is a list of every unit we own, by Purple Air's ID number
unitslist = '12210|12206|12186|12212|12192|12204|12168|12156|12208|12190|144678|'\
            '12178|12188|1224|1202|25985|1220|144676|1228|1236|10754|10766|41235'
#        |12184|12214|12166|1198|1206|12160' Lost/Missing Units
# Shorter list for testing only
#unitslist = '12210|12186|12212'

def readini():
    '''
    A Windows-style .ini file of the same name as this program is read during startup
    to establish the most common configuration options.  Default values are established
    where possible so the user need not declare them.  After the file is read and
    processed, it is overwritten with a new one showing both the values selected as
    well as the default values that were implied.
    '''
    # The .ini parameters are exposed as globals to be available throughout the
    # program.
    global corrected, extentN, extentS, extentE, extentW, units
    global begindate, enddate, begindt, enddt, interval
    global plainjson, datajson, thingspeak, api
    global overwritejson, verbose 
    defaults = {
        'corrected':    'False',
        'extentN':      '42.983',
        'extentS':      '42.916',
        'extentE':      '-72.258',
        'extentW':      '-72.332',
        'units':        '',
        'begindate':    '',
        'enddate':      '',
        'interval':     '10',
        'plainjson':    'False',
        'datajson':     'False',
        'thingspeak':   'False',
        'api':          'False',
        'overwritejson':'False',
        'verbose':     'False' }
    import configparser
    config = configparser.ConfigParser(defaults,allow_no_value=True)
    config.add_section('Main')
    # Look for the .ini file in same directory as the .py source
    try:
        f = open ("Fetch.ini", 'r')
        config.readfp(f)
        f.close()
    except:
        pass
    f = open ("Fetch.ini", 'w')
    config.write(f)

    items = {x[0]:x[1] for x in config.items('Main')}
    corrected   = items['corrected'] == 'True'  # Correct PM data values before output
    extentN     = float(items['extentn'])      # Map extents to look inside
    extentS     = float(items['extents'])      # "
    extentE     = float(items['extente'])      # "
    extentW     = float(items['extentw'])      # "
    units       = str(items['units'])
    begindate   = items['begindate']
    enddate     = items['enddate']
    interval    = items['interval']
    plainjson   = items['plainjson'] == 'True'
    datajson    = items['datajson'] == 'True'
    thingspeak  = items['thingspeak'] == 'True'
    api         = items['api'] == 'True'
    overwritejson= items['overwritejson'] == 'True'
    verbose    = items['verbose'] == 'True'
    global unitslist
    if len(units) > 0:
        unitslist = units
#    print (items['units'], units, unitslist)
    if len(begindate) >0:
        begindt = datetime.datetime.strptime(begindate, '%m/%d/%y')
    if len(enddate) >0:
        enddt = datetime.datetime.strptime(enddate, '%m/%d/%y')
#    print (begindt, enddt)
    print ("Fetch.ini values:")
    for item in sorted( items.keys() ):
        print ("%-12s = %s" % (item, items[item]) )

def doplainjson():
    print ('''\n**************************
    Plain json interface.
    Query http://www.purpleair.com/json with a predefined list of units
    known to exist.  Produce a properly formatted statement which can be 
    pasted into the MapMaker.ini file.
    Query results stored in file FetchPlainjson.json
    ''')
    print ('Units queried:\n' + unitslist)
    # A report showing selected units is printed, along with a properly formatted statement 
    # which can be copy and pasted into the MapMaker.ini file.
    #
    url = "http://www.purpleair.com/json?show=" + unitslist
    f = urllib.request.urlopen (url)
    buff = f.read(); f.close()
    out = open ("FetchPlainjson.json","wb")
    out.write(buff); out.close()

    j = json.loads(buff) 
    r = j['results']
    outtbl = []
    for row in r:
        try:
            if True:  ##( (row['Lat'] >= extentS and row['Lat'] <= extentN) and \
                      ##(row['Lon'] <= extentE and row['Lon'] >= extentW) ):
                outtbl.append (row)
        except:
            continue

    outtbl.sort(key=lambda x: x["Label"])
#    print ("Within the extents Latitude: %9.5f to %9.5f and Logitude %-9.5f to %-9.5f"
#               % (extentN, extentS, extentE, extentW))
    print ("The following PurpleAir units were found:")
    print ("ID     Name            Lat        Lon       Last Seen At    Ver   PmA")
    msg = ' '        
    for row in outtbl:
        ID = row['ID']
        seen =  time.strftime( '%m/%d/%y %H:%M', time.localtime(row["LastSeen"]) )
        if row['Label'][-1:] != 'B':
            print ("%6s %-15s %-9.5f %-9.5f  %-10s  %s  %s" %
                (row['ID'], row['Label'][:15], row['Lat'],
                row['Lon'],seen, row['Version'],
                row['PM2_5Value']))
            msg = msg + str(ID) + ', '
    msg = msg[:-2]
    print ("\nCut and Paste into Purple.ini:\nunits =  " + msg)

def dodatajson():
    print ('''\n**************************
    Data.json interface.
    Search the entire database at http://www.purpleair.com/data.json for units
    that fall within the lat/lon extents.  The database is stored at FetchDataUnfiltered.json
    Search results stored in file FetchDatajson.json
    Units that have not responded in a year or so are dropped from the server.
    ''')
    if overwritejson:
        url = "http://www.purpleair.com/data.json" # Undocumented alternate 
        f = urllib.request.urlopen (url)
        buff = f.read(); f.close()
        out = open ("FetchDataUnfiltered.json","wb")
        out.write(buff); out.close()
    else:
        f = open ("FetchDataUnfiltered.json","rb")
        buff = f.read(); f.close()
        buff = buff.replace('[],', '')  # In May '22 they began generating invalid JSON

    j = json.loads(buff) 
    fields = j['fields']
    data = j['data']
    outtbl = []
    for line in data:
        row = dict(zip(fields,line))
        try:
            if ( (row['Lat'] >= extentS and row['Lat'] <= extentN) and \
                 (row['Lon'] <= extentE and row['Lon'] >= extentW) ):
                outtbl.append (row)
        except:
            continue
    outtbl.sort(key=lambda x: x["Label"])
    print ("Within the extents Latitude: %9.5f to %9.5f and Logitude %-9.5f to %-9.5f"
               % (extentN, extentS, extentE, extentW))
    print ("The following PurpleAir units were found:")
    print ("ID       Name              Lat        Lon     Age in Minutes")

    msg = ' '        
    for row in outtbl:
        ID = row['ID']
        if row['Label'][-1:] != 'B':
            print ("%6s   %-15s %-9.5f %-9.5f  %-5s" %
                (row['ID'], row['Label'][:15], row['Lat'],
                row['Lon'], row['age']))
            msg = msg + str(ID) + ', '
        else:
            print ()
    # Save the collected records in a new JSON file.  The Firefox web browser will
    # display this file nicely in human readable form.
    f = open ("FetchDatajson.json","w")
    f.write('{"jc":')            # Add a preamable to ensure correct JSON syntax
    json.dump(outtbl,f)
    f.write('}')           #  Close the JSON syntax correctly
    f.close()
    msg = msg[:-2]
    print ("\nCut and Paste into Purple.ini:\nunits =  " + msg)


def dothingspeak():
    if not api:  # if it wasn't run, do it now
        doAPI()
    print ('''\n**************************
    Thingspeak interface.
    Query https://api.thingspeak.com/channels/ with the list of units
    output from the Plain json interface function of this program.
    Query results stored in file FetchThingspeak.json
    ''')
    if 'begindt' in globals():
        span = '&start='+begindt.strftime('%Y-%m-%d')+'%2000:00:00'
        span += '&end='+enddt.strftime('%Y-%m-%d')+'%2000:00:00'
        span += '&timescale='+interval + '&results=30'
    else:
        span = '&results=1'

    f = open ("FetchAPI.json","rb")
    buff = f.read(); f.close()
    k = json.loads(buff) 
    outbuff = []
    for line in k['jc']:
#        pp(line)
        url = 'https://api.thingspeak.com/channels/'
        url += str(line['sensor']['primary_id_a'])
        url += '/feeds.json?api_key='
        url += line['sensor']['primary_key_a']
        url += span

        f = urllib.request.urlopen (url)
        buff = f.read(); f.close()
        j = json.loads(buff)
        outbuff.append( j )

        hdr = j['channel']      # Get header data
        print ("\nID      Unit    Channel MAC4          Lat       Lon")
        print ("%6s  %6s  %6s  %-13s %-9.5f %-9.5f" %
            (line['sensor']['sensor_index'], line['sensor']['name'][:6], hdr['id'], hdr['name'][-12:], float(hdr['latitude']),
            float(hdr['longitude'])))
        feed = j['feeds']
        print ('created_at             Temp    Humidity   PM2.5 (CF=1)')
        for row in feed:
            formatstring = '%Y-%m-%dT%H:%M:%SZ'              # Times can be naive or aware of timezones
                                                             # Convert string to naieve  datetime obj
            t = datetime.datetime.strptime(row['created_at'], formatstring) 
            t = pytz.timezone('UTC').localize(t)            # Attach UTC timezone to make it aware
            t = t.astimezone(pytz.timezone('US/Eastern'))   # Rephrase as Eastern time
            t = t.strftime('%m/%d/%y %H:%M') 
            print ('%10s %11s %8s %12s' %
                (t, row['field6'], row['field7'], row['field8']) )
    out = open ("FetchThingspeak.json","w")
    out.write('{"jc":')            # Add a preamable to ensure correct JSON syntax
    json.dump(outbuff, out)
    out.write('}')           #  Close the JSON syntax correctly
    out.close()

def doAPI():
    print ('''\n**************************
    New Improved API interface.
    Query https://api.purpleair.com/v1/sensors/ with a predefined list of units
    known to exist, and credentials as api_key. Produce a properly formatted
    statement which can be pasted into the MapMaker.ini file.
    Query results stored in file FetchAPI.json
    Example:  https://api.purpleair.com/v1/sensors/1220?
                api_key=1F29022F-5079-11EB-9893-42010A8001E8
    ''')
    # A report showing selected units is printed, along with a properly formatted statement 
    # which can be copy and pasted into the MapMaker.ini file.
    #
    out = open ("FetchAPI.json","w")
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
        try:
            if ( (row['latitude'] >= extentS and row['latitude'] <= extentN) and \
                 (row['longitude'] <= extentE and row['longitude'] >= extentW) ):
                outtbl.append (row)
        except:
            continue 
    out.write('{"jc":')            # Add a preamable to ensure correct JSON syntax
    json.dump(outbuff, out)
    out.write('}')           #  Close the JSON syntax correctly
    out.close() 
    print ("Within the extents Latitude: %9.5f to %9.5f and Logitude %-9.5f to %-9.5f"
               % (extentN, extentS, extentE, extentW))
    print ("The following PurpleAir units were found:")
    print ("ID     Name            Lat        Lon       Last Seen At    Ver   ChanID  Key")
    msg = ' '        
    outtbl.sort(key=lambda x: x["name"])
    for row in outtbl:
        ID = row['sensor_index']
        seen =  time.strftime( '%m/%d/%y %H:%M', time.localtime(row["last_seen"]) )
        print ("%6s %-15s %-9.5f %-9.5f  %-10s  %s  %s  %s" %
            (row['sensor_index'], row['name'][:15], row['latitude'],
            row['longitude'],seen, row['firmware_version'],
            row['primary_id_a'], row['primary_key_a']))
        msg = msg + str(ID) + ', '
    msg = msg[:-2]
    print ("\nCut and Paste into Purple.ini:\nunits =  " + msg)


def main():
    print ('''
    Fetch - PurpleAir Sensor Finder Program.
    Before running edit Fetch.ini in same directory.
    Specify which Purple Air servers to query, and
    selection criteria.  If no Fetch.ini file exists,
    one is created with all default specifications.
    ''')
    readini()
    if plainjson: # doplainjson()
        print ('\n The Plain JSON server is no longer available')
    if datajson: # dodatajson()
        print ('\n The Data JSON server is no longer available')
    if api: doAPI()
    if thingspeak: dothingspeak()
    print ("Program completed successfully")
    response = input("Press ENTER to exit the program.") 

main()


