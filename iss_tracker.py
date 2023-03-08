import requests
import json
import xmltodict
from flask import Flask, request
from typing import List
from geopy.geocoders import Nominatim
import math
import time

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
data = {}
MEAN_EARTH_RADIUS = 6371 

def getData()-> List[dict]:
    """
    Retrieves the data from the NASA URL as an XML and returns it as a dictionary.

    Args:
        N/A

    Returns:
        N/A
    """
    url='https://nasa-public-data.s3.amazonaws.com/iss-coords/current/ISS_OEM/ISS.OEM_J2K_EPH.xml'
    response = requests.get(url)
    global data
    data = xmltodict.parse(response.text)

@app.route('/', methods=['GET'])
def showData() -> List[dict]:
    """
    Displays all of the data in the data set from the NASA ISS trajectory data

    Args:
        N/A
    Returns:
        data (dict): Returns all data within the data set from the NASA ISS trajectory data as a list of dictionaries
    """
    if not bool(data):
        return 'Data has been cleared.\n'
    return data

@app.route('/epochs', methods=['GET'])
def showEpochs() -> List:
    """
    Retrieves all of the epochs in the data set from the NASA ISS trajectory data

    Args:
        N/A
    Returns:
        epochs (list): Returns all epochs within the data set from the NASA ISS trajectory data as a list
    """    
    offset = request.args.get('offset', 0)
    limit = request.args.get('limit',0)
    if not bool(data):
        return 'Data has been cleared.\n'

    if offset:
        try: 
            offset = int(offset)
        except ValueError:
            return ("Bad input; please specify a positive integer for offset.", 400)
    if limit:
        try:
            limit = int(limit)
        except ValueError:
            return ("Bad input; please specify a positive integer for limit.", 400)   

    epochs = []
    for x in data['ndm']['oem']['body']['segment']['data']['stateVector']:
        epochs.append(x['EPOCH'])
    if offset != 0 and limit != 0:
        epochs = epochs[offset:(offset+limit)]
    elif offset == 0 and limit != 0:
        epochs = epochs[:(offset+limit)]
    elif offset != 0 and limit == 0:
        epochs = epochs[offset:]
    else:
        epochs = epochs
    return epochs

@app.route('/epochs/<epoch>', methods=['GET'])
def showStateVectors(epoch: str) -> List[dict]:
    """
    Retrieves the position and velocity data of a certain epoch from the NASA ISS trajectory data by using the getEpochInfo function.

    Args:
        epoch (str): A moment in time used as a reference point for some time-varying astronomical quantity -- positional and velocity data for the ISS
    Returns:
        StateVec (List[dict]): Returns position in the X, Y, Z directions as a dictionary
    """
    if not bool(data):
        return 'Data has been cleared.\n'

    for x in data['ndm']['oem']['body']['segment']['data']['stateVector']:
        if x['EPOCH'] == epoch:
            return json.dumps(x,indent=2)
    else:
        return f'Epoch {epoch} cannot be found in the data set\n'

@app.route('/epochs/<epoch>/speed', methods=['GET'])
def showSpeed(epoch: str) -> List[dict]:
    """
    Calculates the speed of the ISS at a given epoch with a x, y, and z velocity. 

    Args:
        epoch (str): A moment in time used as a reference point for some time-varying astronomical quantity -- positional and velocity data for the ISS
    Returns:
        speed (List[dict]): Returns the speed of the ISS from Cartesian velocity vectors
    """
    if not bool(data):
        return 'Data has been cleared.\n'

    for x in data['ndm']['oem']['body']['segment']['data']['stateVector']:
        if x['EPOCH'] == epoch:
            stateVec = json.dumps(x,indent=2)
            x_dot = float(x['X_DOT']['#text'])
            y_dot = float(x['Y_DOT']['#text'])
            z_dot = float(x['Z_DOT']['#text'])
            speed = math.sqrt(x_dot**2+y_dot**2+z_dot**2)
            return {'Speed': {'#text':speed, '@units': 'km/s'}}
    else:
        return f'Epoch {epoch} was not found in the data set\n'

@app.route('/help', methods=['GET'])
def appHelp() -> str:
    """
    Returns help text (as a string) that briefly describes each route
    """
    info = """Try the following routes:
    /                               GET     Return entire data set
    /epochs                         GET     Return list of all Epochs in the data set
    /epochs?limit=int&offset=int    GET     Return modified list of Epochs given query parameters
    /epochs/<epoch>                 GET     Return state vectors for a specific Epoch from the data set
    /epochs/<epoch>/speed           GET     Return instantaneous speed for a specific Epoch in the data set
    /help                           GET     Return help text (as a string) that briefly describes each route
    /delete-data                    DELETE  Delete all data from the dictionary object
    /post-data                      POST    Reload the dictionary object with data from the web\n"""
    return info

@app.route('/delete-data', methods=['DELETE'])
def deleteData() -> str:
    """
    Delete all data from the dictionary object
    """
    global data
    data.clear()
    return 'The data has now been cleared\n'

@app.route('/post-data', methods=['POST'])
def postData() -> str:
    """
    Reload the dictionary object with data from the web
    """  
    global data
    getData()
    return 'The data has now been reloaded to dictionary\n'

@app.route('/comment', methods=['GET'])
def xmlComments():
    """
    Returns the ‘comment’ list object from the ISS data
    """  
    if not bool(data):
        return 'Data has been cleared.\n'

    return data['ndm']['oem']['body']['segment']['data']['COMMENT']

@app.route('/header', methods=['GET'])
def xmlHeader():
    """
    Returns the ‘header’ dict object from the ISS data
    """  
    if not bool(data):
        return 'Data has been cleared.\n'

    return data['ndm']['oem']['header']   

@app.route('/metadata', methods=['GET'])
def xmlMetadata():
    """
    Returns the ‘header’ dict object from the ISS data
    """  
    if not bool(data):
        return 'Data has been cleared.\n'

    return data['ndm']['oem']['body']['segment']['metadata']  

@app.route('/epochs/<epoch>/location', methods=['GET'])
def getLocation(epoch):
    """
    Identifies the latitude, longitude, and geographical location based on the latitude and longitude of the ISS at a given epoch with a x, y, and z velocity. 

    Args:
        epoch (str): A moment in time used as a reference point for some time-varying astronomical quantity -- positional and velocity data for the ISS
    Returns:
        Info (List[dict]): Returns the latitude, longitude, altitude, and geoposition for given Epoch of the ISS from Cartesian position vectors
    """
    if not bool(data):
        return 'Data has been cleared.\n'

    for i in data['ndm']['oem']['body']['segment']['data']['stateVector']:
        if i['EPOCH'] == epoch:
            stateVec = json.dumps(i,indent=4)
            x = float(i['X']['#text'])
            y = float(i['Y']['#text'])
            z = float(i['Z']['#text'])
            hrs = float(epoch[9:-11])
            mins = float(epoch[12:-8])

            lat = math.degrees(math.atan2(z, math.sqrt(x**2 + y**2)))                
            lon = math.degrees(math.atan2(y, x)) - ((hrs-12)+(mins/60))*(360/24) + 24
            if (lon <= 180 and lon >= -180):
                lon = lon
            else:
                lon = -180+(lon-180)
            alt = math.sqrt(x**2 + y**2 + z**2) - MEAN_EARTH_RADIUS 
            
            geocoder = Nominatim(user_agent='iss_tracker')
            geoloc = geocoder.reverse((lat, lon), zoom=1, language='en')

            if geoloc == None:
                return {'Location': {'Latitude' :lat, 'Longitude': lon, 'altitude': { 'value': alt, 'units': 'km'}, 'geo': 'Location may be over the ocean'}}
            else:
                return {'Location': {'Latitude' :lat, 'Longitude': lon, 'altitude': { 'value': alt, 'units': 'km'}, 'geo': str(geoloc)}}
    else:
        return f'Epoch {epoch} was not found in the data set\n' 

@app.route('/now', methods=['GET'])
def getNowLoc():
    """
    Identifies the epoch that is closest to the current stime and returns the latitude, longitude, geographical location based on the latitude and longitude, and speed of the ISS with a x, y, and z position and velocity. 

    Args:
        epoch (str): A moment in time used as a reference point for some time-varying astronomical quantity -- positional and velocity data for the ISS
    Returns:
        Info (List[dict]): Returns the latitude, longitude, altitude, and geoposition for given Epoch of the ISS from Cartesian position vectors
    """ 
    if not bool(data):
        return 'Data has been cleared.\n'

    time_now = time.time()         # gives present time in seconds since unix epoch
    smallest_diff = float('inf')
    
    state_vector = data['ndm']['oem']['body']['segment']['data']['stateVector']
    
    smallest_diff = float('inf')
    
    for i in range(len(state_vector)):
        sv = state_vector[i]
        epoch = sv['EPOCH']
        epoch_time = time.mktime(time.strptime(epoch[:-5], '%Y-%jT%H:%M:%S'))
        diff = epoch_time - time_now
        if abs(diff) < smallest_diff:
            smallest_diff = abs(diff)
            now_epoch = epoch

    for i in data['ndm']['oem']['body']['segment']['data']['stateVector']:
        if i['EPOCH'] == now_epoch:
            stateVec = json.dumps(i,indent=4)
            x = float(i['X']['#text'])
            y = float(i['Y']['#text'])
            z = float(i['Z']['#text'])
            hrs = float(epoch[9:-11])
            mins = float(epoch[12:-8])

            lat = math.degrees(math.atan2(z, math.sqrt(x**2 + y**2)))                
            lon = math.degrees(math.atan2(y, x)) - ((hrs-12)+(mins/60))*(360/24) + 24
            if (lon <= 180 and lon >= -180):
                lon = lon
            else:
                lon = -180+(lon-180)

            alt = math.sqrt(x**2 + y**2 + z**2) - MEAN_EARTH_RADIUS

            geocoder = Nominatim(user_agent='iss_tracker')
            geoloc = geocoder.reverse((lat, lon), zoom=10, language='en')

            x_dot = float(i['X_DOT']['#text'])
            y_dot = float(i['Y_DOT']['#text'])
            z_dot = float(i['Z_DOT']['#text'])
            speed = math.sqrt(x_dot**2+y_dot**2+z_dot**2)

            if geoloc == None:
                return {'Closest_epoch': now_epoch, 'epochTime':epoch_time, 'Seconds_from_now': smallest_diff,'Location': {'Latitude' :lat, 'Longitude': lon, 'altitude': { 'value': alt, 'units': 'km'}, 'geo': 'Location may be over the ocean'},'Speed': {'#text': speed, '@units': 'km/s'}}
            else:
                return {'Closest_epoch': now_epoch, 'epochTime':epoch_time, 'Seconds_from_now': smallest_diff,'Location': {'Latitude' :lat, 'Longitude': lon, 'altitude': { 'value': alt, 'units': 'km'}, 'geo': str(geoloc)},'Speed': {'#text': speed, '@units': 'km/s'}} #{'Location': {'Latitude':lat, '@units': 'deg'}}
            
    else:
        return f'Epoch {epoch} was not found in the data set\n'


if __name__ == '__main__':
    getData()
    app.run(debug=True, host='0.0.0.0')
