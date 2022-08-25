'''
#
# Overall flow of this program is documented at the very bottom where execution
# begins. Below, all functions functions are defined before use.
#
'''

import arcpy, urllib.request, json, datetime, csv, os
from ftplib import FTP
import smtplib
from email.mime.text import MIMEText

arcpy.env.overwriteOutput=True
arcpy.CheckOutExtension ('Spatial')  # Needed for arcpy.gp.Idw_sa
#from pprint import pprint as pp

#global variable used by makemap() and provided in gatherdata() or archmain()
weathertext = ''

def PurpleAirDataCorrection(pm):
    '''
    Liner correction function provided by Nora Traviss to adjust the PM2.5 value
    reported by PurpleAir units.  Used ONLY to adjust raw data values prior to
    generating the map.  Uncorrected raw values are saved to the .csv archive.
    '''
    pm = round(0.428 * float(pm) +0.58, 2)
    return pm


def HumidityCalc(temp_c, dewpoint_c):
    '''
    Fuction to convert the temp/dewpoint reported by the airport weather server into
    percent humidity.
    '''
    from math import exp
    temp_c = float(temp_c)
    dewpoint_c = float(dewpoint_c)
    h = 100*(exp( (17.625*dewpoint_c)/(243.04+dewpoint_c) ) / exp( (17.625*temp_c)/(243.04+temp_c) ))
    return round(h,0)


def gatherdata(csvarchive, timestamp):
    '''
    Each time called, create a new empty PurplePoints.csv file to receive data to be mapped and insert a
    header row. Then:
    . Insert a zero value point at the four corners of the map because the IDW mapping
      function can produce strange results over areas with undefined data.
    . Poll the PurpleAir units over the Internet and append the data received to a
      .csv archive file.
    . If the reported values pass a series of validity tests then write the lat/lon and
      PM2.5 value to PurplePoints.csv
    . Fetch and decode current conditions from the local airport weather server and
      append to the .csv archive file.
    . Prepare a weather text message that will be used by makemap().
    #
    Note that all entries in the .csv archive file for a given map set bear the same
    timestamp in the first column even though individually they may reflect slightly
    different times.  This makes it possible for subsequent users to reassemble them as
    a single related block.
    '''
    global weathertext
    csvcurrentfile = open('PurplePoints.csv', 'w', newline='')
    csvcurrent = csv.writer(csvcurrentfile)
    csvcurrent.writerow (['time', 'name', 'lat', 'lon', 'pm'])
    csvcurrent.writerow([timestamp, 'UpperLeft',  extentN, extentW, 0])
    csvcurrent.writerow([timestamp, 'UpperRight', extentN, extentE, 0])
    csvcurrent.writerow([timestamp, 'LowerLeft',  extentS, extentW, 0])
    csvcurrent.writerow([timestamp, 'LowerRight', extentS, extentE, 0])

    # Poll each PurpleAir unit in turn from the list in MapMaker.ini using the unique
    # ID number.  See manufacturer's document "Using PurpleAir Data.pdf"
    for unit in units.split(', '):
        try:
            url = "http://www.purpleair.com/json?show="+unit.strip()
            f = urllib.request.urlopen (url)
            buff = f.read()
            j = json.loads(buff)
        except:
            continue

        # Each PurpleAir unit has two independent sensors, and we capture the data
        # from them in buffers named r and r1
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


        # Set the error code based on a few validity tests:
        # 0 = no errors
        # REPLACED:  1 = The A and B units disagree by more than 10
        # 1 = The A and B units disagree by more than 50% of the lower value
        #    AND differ by more than 10
        # 2 = Reported value is unreasonable, over 250
        # 4 = Data reported is over 35 minutes old
        # codes are additive so possible values range 0-7
        errorcode = 0
        if (float(pm)>0.0) & (float(pm1)>0.0):  # Test only if both > zero
            if (not( (2/3 <= float(pm)/float(pm1) <= 3/2) )) & (abs(float(pm)-float(pm1)) > 10):  # If one exceeds 150% of the other
                errorcode = errorcode + 1
        if float(pm) > 250:
            errorcode = errorcode + 2
        if time.time() - r["LastSeen"] > 60*35:
            errorcode = errorcode + 4
        csvarchive.writerow ([timestamp, r['Label'], r['Lat'], r['Lon'], seen, pm, pm1, pressure, temp_f, humidity, s['v'], s['v1'], s['v2'], s['v3'], s['v4'], s['v5'], s['v6'], errorcode])

        # Save all data to the .csv archive, but map only error-free data from
        # non-excluded units
        statstable[unit]['Label'] = r['Label']
        if (errorcode == 0):
            pm = PurpleAirDataCorrection(s['v1'])
            csvcurrent.writerow([ timestamp, r['Label'], r['Lat'], r['Lon'], pm ])
        else:
            statstable[unit]['errors'] += 1
                
    try:
        url = "https://aviationweather.gov/adds/dataserver_current/httpparam?dataSource=metars&requestType=retrieve&format=csv&stationString=KEEN&hoursBeforeNow=2&mostRecent=True"
        f = urllib.request.urlopen (url)

        buff = []
        for line in f:
            line = line.decode("utf-8")
            if ',' in line:
                buff.append (line)
        f.close()
        #The Python csv library can't handle fields with duplicate names, so add a suffix to each
        buff[0] = buff[0].replace('sky_cover,','sky_cover0,', 1)
        buff[0] = buff[0].replace('sky_cover,','sky_cover1,', 1)
        buff[0] = buff[0].replace('sky_cover,','sky_cover2,', 1)
        buff[0] = buff[0].replace('sky_cover,','sky_cover3,', 1)
        buff[0] = buff[0].replace('cloud_base_ft_agl,','cloud_base_ft_agl0,', 1)
        buff[0] = buff[0].replace('cloud_base_ft_agl,','cloud_base_ft_agl1,', 1)
        buff[0] = buff[0].replace('cloud_base_ft_agl,','cloud_base_ft_agl2,', 1)
        buff[0] = buff[0].replace('cloud_base_ft_agl,','cloud_base_ft_agl3,', 1)

        reader = csv.DictReader(buff)
#        row = reader.next()    #deprecated with Python 3
#        for row in reader:
#            pass
# The above two lines work but should be:    row=next(reader)
        row=next(reader)
        try:        # If we are missing values for temp and dewpoint default to nothing
            row['humidity'] = str( HumidityCalc(row['temp_c'], row['dewpoint_c']) )
        except:
            row['humidity'] = ''
        csvarchive.writerow ( [ timestamp, row['raw_text'], row['latitude'], row['longitude'],
            row['wind_dir_degrees'], row['wind_speed_kt'], row['wind_gust_kt'], row['altim_in_hg'], row['temp_c'],
            row['humidity'], row['dewpoint_c'], row['visibility_statute_mi'], row['wx_string'],
            row['sky_cover0'], row['cloud_base_ft_agl0'], row['sky_cover1'], row['cloud_base_ft_agl1'],
            row['sky_cover2'], row['cloud_base_ft_agl2'], row['sky_cover3'], row['cloud_base_ft_agl3'] ] )
        weathertext = '\nTemperature Celcius: ' + row['temp_c'] + \
                      '<br>\nHumidity: ' + row['humidity'] +  \
                      '<br>\nWind Direction: ' + row['wind_dir_degrees'] + \
                      '<br>\nWind Speed/Gust: ' + \
                      row['wind_speed_kt'] + '/' + \
                      row['wind_gust_kt']
    except:
        print ('Weather read failure')
        weathertext = ''
    csvcurrentfile.close()

"""
def gatherarchdata(buff, timestamp):
    '''
    Emulate gatherdata() by taking data from a memory buffer created in archmain() rather than gathering it
    from the Internet.
    '''
    csvcurrentfile = open('PurplePoints.csv', 'w', newline='')
    csvcurrent = csv.writer(csvcurrentfile)
    csvcurrent.writerow (['time', 'name', 'lat', 'lon', 'pm'])
    csvcurrent.writerow([timestamp, 'UpperLeft',  extentN, extentW, 0])
    csvcurrent.writerow([timestamp, 'UpperRight', extentN, extentE, 0])
    csvcurrent.writerow([timestamp, 'LowerLeft',  extentS, extentW, 0])
    csvcurrent.writerow([timestamp, 'LowerRight', extentS, extentE, 0])
    for row in buff:
        pm = PurpleAirDataCorrection(row['pmA'])
        csvcurrent.writerow([timestamp, row['name'], row['lat'], row['lon'], pm])
    csvcurrentfile.close()
"""

def makemap(datedname):
    '''
    Using the arcpy Python extensions to ESRI ArcMap:
    . Convert the PurplePoints.csv data prepared by gatherdata() to a GIS layer of
      lat/lon points, each bearing a corrected PM2.5 value.
    . Execute the existing inverse distance weighted layer function "./Data/jcIDW"
      causing it to refresh its output using the updated lat/lon points layer.
    . Insert the prepared weathertext message into the bottom margin of the map.
    . Insert a bold timestamp into the lower left corner of the map.
    . Execute the existing MapMaker.mxd project to produce a .jpg image map in the maps
      directory.
    (Note: comments above refer to older ArcMap - this code is updated to ArcGIS Pro)
    '''
    wtext = '<p style="font-size:20px;padding-left:15px">' + weathertext
    with open (outdir + 'weather.html', 'w') as f:
        f.write(wtext)

    x = time.strptime(datedname[0:15],'%Y_%m_%d_%H%M')
    wkday = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][x.tm_wday]
    timetext = '%s %d/%d/%d\n%02d:%02d'%(wkday, x.tm_mon, x.tm_mday, x.tm_year, x.tm_hour, x.tm_min)


    arcpy.MakeXYEventLayer_management(table="PurplePoints.csv", in_x_field="lon", in_y_field="lat", out_layer="jcLayer")
    idwraster = arcpy.sa.Idw("jcLayer", "pm", "2.68000000000001E-04")
    idwraster.save("./Data/jcIDW")

    aprx = arcpy.mp.ArcGISProject(r"MapMaker.aprx")
    layout = aprx.listLayouts("new")[0]
    timestamp = layout.listElements("TEXT_ELEMENT", "timestamp")[0]
    timestamp.text = timetext 
    # the output map image file  is named like:   2018_11_12_1606.jpg
    jpg = outdir + datedname
    layout.exportToJPEG(jpg, resolution=int(jpegres), jpeg_quality=int(jpegqual))


def makemovie():
    '''
    Using the open source tool FFMPEG  -  https://ffmpeg.org/
    assemble all the .jpg images found in the map directory into a .mp4 video.
    Parameters are taken from MapMaker.ini to control image quality and frame rate.

    . On startup, a separate subprocess instance of FFMPEG  named "mov" is established
      to read raw images from its STDIN and append them to a .mp4 output file.

    . For each .jpg file found in the maps directory, a new instance of FFMPEG named
      "jpg" is started to read the .jpg and pipe the raw image data to an array in
      memory.  Each memory image is written to STDIN of the "mov" process.

    . After the last .jpg file has been processed, the inputs to the "mov" process are
      closed, causing it to write the .mp4 file then exit.
    '''
    import subprocess
    command =  ['ffmpeg.exe', '-y',
            '-framerate', framerate,
            '-i', '-',
            '-pix_fmt', 'yuv420p',
            #            '-s', '816x1056',
            outdir + 'Current_Conditions.mp4']
    mov = subprocess.Popen(command,
            stdout = subprocess.PIPE,
            stdin = subprocess.PIPE,
            stderr = subprocess.PIPE,
            bufsize = 816*1056*3)
    localfiles = []
    for f in os.listdir(outdir):
        f = outdir + f
        t = os.stat(f).st_mtime
        if f[-4:] == '.jpg': localfiles.append ((f,t))

    localfiles = sorted(localfiles, key = lambda x : x[1])
    for row in localfiles:
        filename = row[0]
        command =  ['ffmpeg.exe',
                '-i', filename,
                #                '-s', '816x1056',
                '-f', 'image2pipe', '-' ]
        jpg = subprocess.Popen(command,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE,
                bufsize = 816*1056*3)
        image = jpg.stdout.read(816*1056*3)
        del jpg
        mov.stdin.write(image)
    mov.stdin.close()
    mov.stdout.close()
    mov.stderr.close()


def ftpresults(datedname,newmovie):
    '''
    Using FTP protocol, transfer the latest .jpg map, .mp4 video and .txt console
    log to the website server.  Subsequent visitors to the website will receive the
    most recent uploads.
    Also, while the connection is open, test for the presence of a file named "stop".
    '''
    ftp = FTP()
    # Last parameter is seconds to time out and give up
    ftp.connect(ftpurl, 21, 120)
    ftp.getwelcome()
    ftp.login(ftpuser, ftppwd)
    ftp.cwd(ftpdir)
    remotefiles = ftp.nlst()
    if saveconsole:
        f = open('MapMakerOut.txt', 'rb')
        ftp.storbinary('STOR MapMakerOut.txt', f)
        f.close()
    if "stop" in remotefiles:
        ftp.delete ('stop')
        return True 
    with open(outdir + 'weather.html', 'rb') as f:
        ftp.storbinary('STOR weather.html', f)
    with open(outdir + datedname, 'rb') as f:
        ftp.storbinary('STOR map.jpg', f)
    if newmovie: 
        with open(outdir + 'Current_Conditions.mp4', 'rb') as f:
            ftp.storbinary('STOR Current_Conditions.mp4', f)
    ftp.quit()
    return False


def cleanup ():
    '''
    Maps are generated and sent to the website every (sampleinterval) typically 10 minutes,
    but images are needed only every (movieinterval) typically 60 minutes for
    generating the video.  And only the images from the most recent (keepdy) days are retained.
    Everything else is deleted.
    '''
    dlimit = time.time() - 60*60*24*float(keepdy)   # Discard maps older than keepdy
    # Make a table of files sorted by time
    localfiles = []
    for f in os.listdir(outdir):
        f =outdir + f
        t = os.stat(f).st_mtime
        if f[-4:] == '.jpg': localfiles.append ((f,t))
    localfiles = sorted(localfiles, key = lambda x : x[1])    # Sort by file creation time
    x = localfiles[-1][1]
    prevframe = 0
    for row in localfiles:

        if row[1] >= dlimit:            # Only keep maps younger than keepdy
                                        # and only one per movieinterval (hour)
            if  prevframe == 0 \
                or row[1] >= prevframe+60*float(movieinterval) \
                or row[1] == x:
                prevframe = row[1]
                continue
        os.remove (row[0])                          # Discard the rest

#        if row[1] < dlimit:                        # Only keep maps younger than keepdy
#            os.remove (row[0])                          # Discard the rest

def sendalert():
    csvcurrentfile = open('PurplePoints.csv', 'r')
    csvcurrent = csv.DictReader(csvcurrentfile)
    avg = high = denom = 0
    for row in csvcurrent:
        pm = float(row['pm'])
        if pm > 0:
            avg += pm
            denom +=1
        if pm > high: high = pm
    csvcurrentfile.close()
    if denom:
        avg = avg/denom
    if avg > float(alertavg) or high > float(alertth): 
        msg = MIMEText("KSC Air Quality Alert")
        msg['From'] = 'jc@Clockery.com'
        msg['subject'] = 'KSC Air Quality Alert'
        s=smtplib.SMTP("smtp.1and1.com:587")
        s.login("jc@Clockery.com", "geochron") 
        s.sendmail("jc@Clockery.com", ["jc@Clockery.com", 'ntraviss@keene.edu'], msg.as_string())
        s.quit()

def sendreport():
        report = '\n%7s %-7.7s %6s\n' % ('Unit', 'Label', 'errors') 
        for row in statstable.keys():
            report +='%7s %-7.7s %6s\n' % (row, statstable[row]['Label'], statstable[row]['errors'])
            statstable[row]['errors'] = 0
#        print (report)
        msg = MIMEText(report)
        msg['From'] = 'jc@Clockery.com'
        msg['subject'] = 'MapMaker 24 hour errors report'
        s=smtplib.SMTP("smtp.1and1.com:587")
        s.login("jc@Clockery.com", "geochron") 
        s.sendmail("jc@Clockery.com", ["jc@Clockery.com", "ntraviss@keene.edu"], msg.as_string())
        s.quit()

"""
def archmain():
    '''
    ##################Program Main Flow in Archive / Research Mode #################

    To use the program in archive mode:
    . Create a file named  "ToBeMapped.csv" in the directory "./ArchMaps/" that contains
        one of each header type plus the rows covering the time period of interest from the
        .csv archive files.
    . Edit MapMaker.ini to include "archmap=True" and run the program.
    . Edit MapMaker.ini to include a value for "movieinterval" specifying the time
      interval between movie frames and hence, .jpg map images desired.

    . The program will reproduce the maps as they were originally displayed on the
        website and store them in the ArchMaps directory.
    . It will then then assemble them all into a .mp4 move also in that directory.

    In this mode the program:
    . Reads rows from the input .csv file, assembling the records from a single timestamp block
    . Calls gatherarchdata() which emulates gatherdata() in preparing data for makemap()
    . After the last map has been created, calls makemovie() which assembles all the
        .jpg map images in "./ArchMaps/" into a single video.
    '''
    global weathertext
    sensorsbuff  = []
    metarbuff   = []
    f = open (outdir + "ToBeMapped.csv", 'r', newline='')
    # Cycle through the input file separating the PurpleAir data rows from the
    # weather data rows into separate tables.
    for line in f:
        if line == '':
            continue
        if 'name' in line:
            sensorsheader = line
            continue
        if 'raw_text' in line:
            metarheader = line
            continue
        if 'KEEN' in line:
            metarbuff.append(line)
        else:
            sensorsbuff.append(line)

    # Sort the PurpleAir data by timestamp and insert the appropriate header row
    sensorsbuff = sorted(sensorsbuff, key = lambda x : x[0:15])
    sensorsbuff.insert (0,sensorsheader)
    # Sort the weather data by timestamp and insert the appropriate header row
    metarbuff =   sorted(metarbuff, key = lambda x : x[0:15])
    metarbuff.insert (0,metarheader)

    sensorsreader = csv.DictReader(sensorsbuff)
    metarreader   = csv.DictReader(metarbuff)
    stopnow = False
    currentimage = '0'
    buff = []
    row = next(sensorsreader)
    metar = next(metarreader)

    # Isolate blocks of records bearing the same timestamp , fetch the corresponding
    # weather record, then submit them to gartherarchdata()
    # Note that not every block is mapped.  Blocks are skipped to create a time
    # interval between images of at least (movieinterval) minutes.
    while not stopnow:
        x = time.strptime(row['time'],'%Y_%m_%d_%H%M')
        rowtime = datetime.datetime(x.tm_year, x.tm_mon, x.tm_mday, x.tm_hour, x.tm_min, x.tm_sec)
        if currentimage == '0':
            currentimage = row['time']
            currentimagetime = rowtime - datetime.timedelta(minutes=int(movieinterval))

        #Skip data up to the next (movieinterval) time block.
        while rowtime < currentimagetime + datetime.timedelta(minutes=int(movieinterval)):
            try:
                row = next(sensorsreader)
                x = time.strptime(row['time'],'%Y_%m_%d_%H%M')
                rowtime = datetime.datetime(x.tm_year, x.tm_mon, x.tm_mday, x.tm_hour, x.tm_min, x.tm_sec)
            except StopIteration:
                break
        currentimage = row['time']
        currentimagetime = rowtime

        # Gather all the records for this timestamp block.
        while row['time'] == currentimage:
            if row['errorcode'] == '0':
                buff.append(row)
            try:
                row = next(sensorsreader)
            except StopIteration:
                stopnow = True
                break

        # Pickup the corresponding weather record and convert to text to be inserted
        # into the map.
        while metar['time'] != currentimage:
            try:
                metar = next(metarreader)
            except StopIteration:
                #metar = BLANKS
                break
        weathertext = '\nTemperature Celcius: ' + metar['temp_c'] + \
                      '\nHumidity: ' + metar['humidity'] +  \
                      '\nWind Direction: ' + metar['wind_dir_degrees'] + \
                      '\nWind Speed/Gust: ' + \
                      metar['wind_speed_kt'] + '/' + \
                      metar['wind_gust_kt'] + \
                      '\n \nARCHIVE MAP SHOWING DATA FOR:\n' + \
                      currentimage

        # Assemble the data for makemap() and submit.
        gatherarchdata(buff, currentimage)
        datedname = currentimage + '.jpg'
        makemap(datedname)
        print ('.', end='', flush=True)
        buff = []

    # All the images have been created, now assemble them into a .mp4 video
    makemovie()
"""

def mapmain():
    '''
    ###############################Program Main Flow in Online Mode #################

    On startup the program creates an empty .csv file to receive archived data
    and inserts two column header rows.
    The first header row describes PurpleAir unit raw data.
    The second header row describes the airport weather data.
    Subsequent users need to use the appropriate header depending on which type of data
    being examined.

    Every (sampleinterval) minutes the program wakes up,
    . Gathers input data from the PurpleAir Sensors and the airport weather server.
    . Commits that data to the .csv archive file.
    . Calls ArcMap to generate a new .jpg map image.
    . If it's been (movieinterval) minutes since the last, make a new movie.
    . Upload the map, movie, and console log to the web server.

     If the ftpresults() function reports the presence of a file named "stop" on the
     web server, it deletes it then this program terminates.  This makes it possible to
     stop the program from anywhere on the Internet without having access to the
     keyboard and console - for example when swapping in a later version from a
     different location.
    '''
    # the history data file is named like:   2018_11_12_1606.csv
    csvarchivefile = open(outdir + time.strftime('%Y_%m_%d_%H%M') + '.csv', 'w', newline='')
    csvarchive = csv.writer(csvarchivefile)
    csvarchive.writerow (['time', 'name', 'lat', 'lon', 'lastseen', 'pmA', 'pmB', 'pressure', 'temp', 'humidity', 'v', 'v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'errorcode'])
    csvarchive.writerow (['time', 'raw_text', 'latitude', 'longitude',
        'wind_dir_degrees', 'wind_speed_kt', 'wind_gust_kt', 'altim_in_hg', 'temp_c',
        'humidity', 'dewpoint_c', 'visibility_statute_mi', 'wx_string',
        'sky_cover0', 'cloud_base_ft_agl0', 'sky_cover1', 'cloud_base_ft_agl1',
        'sky_cover2', 'cloud_base_ft_agl2', 'sky_cover3', 'cloud_base_ft_agl3'])
    lastmovie =  -1
    lastalert = -1
    newmovie = False
    stopnow = False
    prtlength = 200

    lastreport = datetime.date.min
    global statstable
    statstable = {}
    for unit in units.split(', '):
        statstable[unit] = {'Label':'', 'errors':0}

    while True:
        try:
            if prtlength > 100:
                print ('\n' +  time.ctime(time.time())[4:16] + ' ', end='', flush=True)
                prtlength = 13
            timestamp  = time.strftime('%Y_%m_%d_%H%M')
            datedname = timestamp + '.jpg'
            gatherdata(csvarchive, timestamp)
            csvarchivefile.flush()
            makemap(datedname)
            print ('.', end='', flush=True); prtlength += 2
            if time.time() > lastmovie + float(movieinterval)*60:
                cleanup()
                makemovie()
                print ('M', end='', flush=True); prtlength += 2
                lastmovie = time.time()
                newmovie = True
            if time.time() > lastalert + float(alertinterval)*60:
                if not testmode: sendalert()
                lastalert = time.time()
            if datetime.date.today() > lastreport :
                if not testmode: sendreport()
                lastreport = datetime.date.today()
            if not testmode: stopnow = ftpresults(datedname,newmovie)
            if stopnow:
                print ('\nStop file detected, quitting.')
                break
            newmovie = False
        except Exception as x:
            print ("\nSomething failed at ", time.ctime( time.time() ) )
            import traceback
            traceback.print_exc()
            print (flush=True)

        sys.stdout.flush()
        sys.stderr.flush()
        time.sleep( 60*float(sampleinterval) )
def readini():
    '''
    A Windows-style .ini file of the same name as this program is read during startup
    to establish the most common configuration options.  Default values are established
    where possible so the user need not declare them.  After the file is read and
    processed, it is overwritten with a new one showing both the values selected as
    well as the default values that were implied.  This extended set of values is also
    written to the console and to the console log file to facilitate troubleshooting.
    '''
    # The .ini parameters are exposed as globals to be available throughout the
    # program.
    global testmode, extentN, extentS, extentE, extentW, units, movieinterval, sampleinterval, keepdy
    global jpegqual, jpegres, ftpurl, ftpuser, ftppwd, ftpdir, saveconsole, framerate
    global alertinterval, alertth, alertavg, archmap
    defaults = {
        'testmode':'False',
        'archmap':'False',
        'saveconsole':'True',
        'sampleinterval':'10',
        'movieinterval':'60',
        'framerate':'1',
        'keepdy':'1',
        'jpegqual':'70',
        'jpegres':'96',
        'alertinterval':'360',
        'alertth':'33',
        'alertavg':'15' 
        }
    import configparser
    config = configparser.ConfigParser(defaults)
    # Look for the .ini file in same directory as the .py source
    f = open ("MapMaker.ini", 'r')
    config.readfp(f)
    f.close()
    f = open ("MapMaker.ini", 'w')
    config.write(f)

    items = {x[0]:x[1] for x in config.items('main')}
    extentN  = items['extentn']     # Map extents and location of zero value corner data points
    extentS  = items['extents']     # "
    extentE  = items['extente']     # "
    extentW  = items['extentw']     # "
    keepdy   = items['keepdy']      # How many days to keep maps before deleting completely
    jpegqual = items['jpegqual']    # JPEG quality value for the map image 0-100
    jpegres  = items['jpegres']     # JPEG DPI resolution for the map image
    units    = items['units']       # List of PurplAir unit IDs to process
    ftpurl   = items['ftpurl']      # FTP connection parameters
    ftpuser  = items['ftpuser']     # "
    ftppwd   = items['ftppwd']      # "
    ftpdir   = items['ftpdir']      # "
    framerate= items['framerate']   # Video frames per second
    sampleinterval = items['sampleinterval']  # Interval in minutes between data samples
    movieinterval  = items['movieinterval']    # Interval in minutes between new movies
    alertinterval  = items['alertinterval']    # Interval in minutes between text alerts
    alertth  = items['alertth']    # Threshold for single unit to alert
    alertavg = items['alertavg'] # Threshold for average of units to alert

    testmode = False                # Causes program to skip website uploads
    if items['testmode'].upper() == "TRUE":
        testmode = True
    archmap = False                 # Determines program run node
#    if items['archmap'].upper() == "TRUE":
#        archmap = True
    saveconsole = False             # Replicate console messages to log file and website
    if items['saveconsole'].upper() == "TRUE":
        saveconsole = True
    return items

class Logger(object):
    '''
    A Logger object can be substituted in place of stdout and stderr
    which will fork messages to a text file then pass them on to the console as usual.
    This log file is mirrored to the website, making it possible to check program status
    from anywhere on the Internet without being present at the computer console.
    '''
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("MapMakerOut.txt", "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
    def flush(self):
        self.terminal.flush()
        self.log.flush()

'''
#################################Execution Begins Here #################

The program runs in two modes -

1) Online mode which collects data from the PurpleAir sensors and the local airport
weather server, writes that data to a .csv archive file, then from the most recent
data creates a .jpg map image and uploads it to the KeeneCleanAir.org website.
Also the most recent 24 .jpg images are assembled into a .mp4 video, also uploaded
to the website.

2) Archive/Research mode that reads rather than writes the .csv archive file and
generates maps and video which are sent not to the website but to a special archive
folder for review by persons wishing to interpret the archived data.

An effort has been made to avoid the necessity of understanding and modifying
Python code in order to select the most likely options by implementing a
Windows-style .ini file.  See detail at  readini()
'''
KeepOld = False

inivalues = readini()
if saveconsole:
    consoloutput = Logger()
    sys.stdout = consoloutput
    sys.stderr = consoloutput
print ("MapMaker.ini values:")
for item in sorted( inivalues.keys() ):
    print ("%-12s = %s" % (item, inivalues[item]) )

# depending on the selection in mapmaker.ini run the program in online or archive
# mode.  Overall flow is controlled by either mapmain() or archmain()
if archmap:
    print ("\nMapMaker programin Archive Print mode\n"\
          "See results in ArchMaps directory.\n" )
#    outdir = "./ArchMaps/"
#    archmain()
    print ("Program completed successfully")
else:
    print ("\nMapMaker program\n"\
          "Results posted online and in Maps directory." )
    outdir = "./Maps/"
    mapmain()

if saveconsole:
    sys.stdout.log.close()
    sys.stdout = sys.stdout.terminal
    sys.stderr =  sys.stderr.terminal
