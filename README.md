# Tracking the ISS

The purpose of this project is to query and return interesting information from the ISS data set provided by NASA. The project has the ability to retrieve all of the information within the Orbit Ephemeris Message dataset, **just** the ephochs, the state vector a specific epoch, the speed of the identified epoch, delete the data, and post the data. At the altitude of the International Space Station (ISS), a sparse atmosphere still exists, which generates resistance that can gradually lead to errors in its anticipated trajectory. To mitigate this, orbital mechanics update the projected trajectory to get the most precise estimation possible. Maintaining accurate trajectory calculations is critical for establishing communication links, scheduling rendezvous with visiting spacecraft, and ensuring the ISS's path remains unobstructed by potential collisions.

## Retrieve Data

The user may view the website that the ISS trajectory data comes from using the link below:

```bash
https://spotthestation.nasa.gov/trajectory_data.cfm
```
The data can be downloaded in ``TXT`` or ``XML`` format. The saved data looks like the following: 

```bash
...
<data>
  <stateVector>
        <EPOCH>2023-048T12:00:00.000Z</EPOCH>
        <X units="km">-5097.51711371908</X>
        <Y units="km">1610.3574036042901</Y>
        <Z units="km">-4194.4848049601396</Z>
        <X_DOT units="km/s">-4.5815461024513304</X_DOT>
        <Y_DOT units="km/s">-4.8951801207083303</Y_DOT>
        <Z_DOT units="km/s">3.70067961081915</Z_DOT>
    </stateVector>
    <stateVector>
        <EPOCH>2023-048T12:04:00.000Z</EPOCH>
        <X units="km">-5998.4652356788401</X>
        <Y units="km">391.26194859011099</Y>
        <Z units="km">-3164.26047476555</Z>
        <X_DOT units="km/s">-2.8799691318087701</X_DOT>
        <Y_DOT units="km/s">-5.2020406581448801</Y_DOT>
        <Z_DOT units="km/s">4.8323394499086101</Z_DOT>
    </stateVector>
    ... etc
```
For this project, the data is downloaded in XML format.

## Installation

To begin, make a new folder for this project.
```console
[user-vm]$ cd ~/coe-332/
[user-vm]$ mkdir docker/
[user-vm]$ cd docker/
[user-vm]$ pwd
/home/ubuntu/coe332/docker
```

Install this project by pulling the image from Docker Hub. Execute the following lines:
```console
[user-vm]$ docker pull alb6443/iss_tracker:hw05
[user-vm]$ docker run -it --rm -p 5000:5000 alb6443/iss_tracker:hw05
 * Serving Flask app 'iss_tracker'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 434-637-715
```
We are now in a container from the image! Before we move on, here is an explanation of the options used above:
```console
docker run                                   # run a container
-it                                          # interactively attach terminal to inside of container
--rm                                         # remove the container after the program exits
-p 5000:5000                                 # map the host port 5000 to the container port 5000
alb6443/iss_tracker:hw05                     # image to use for the container
```
When that command gets cumbersome and complex, it is much simpler to call 
```console
[user-vm]$ docker-compose up
```
If you want to build your own image, use the following commands:
```console
[user-vm]$ docker build -t <dockerhubusername>/<code>:<version> .   # builds Docker image
[user-vm]$ docker-compose up --build    # launches the container and forces a the image to rebuild
```
This will build a Docker image that you can spin up using one of the previously mentioned commands. 

You now have access to all of the routes detailed below. For more information, [go to Make a Request section](#make-a-request).

## Understanding the Scripts

This project has one script-- ``iss_tracker.py`` 

**``iss_tracker.py``**: This script is a Flask application that has four routes: ``/``, ``/epochs?limit=int&offset=int``, ``/epochs/<epoch>``, ``/epochs/<epoch>/speed``, ``/epochs/<epoch>/location``, ``/help``, ``/delete-data``, ``/post-data``, ``/comment``, ``/header``, ``/now``, and ``/metadata``. In addition the Flask application utilizes one functions outside of the routes: ``getData``. The function and routes are explained in further detail below:

### Functions
**``getData()``**: This function is designed to retrieve the data from the NASA URL as an XML and stores it as a list of dictionaries. 

### Make a Request
Open a separate terminal window for the next step. To make a request to your Flask app, type the following in the new terminal:

```console
[user-vm]$ curl localhost:5000/
```
All of the Epoch data from the NASA website will populate. To retrieve other data, familiarize yourself with the other routes detailed in the table below:

<table>
<tr>
<td> Route </td> <td> Description and output</td>
</tr>
<tr>
<td> <code>/</code> </td>
<td>

The entire data set
```json
...{
    "EPOCH": "2023-063T11:51:00.000Z",
    "X": {
        "#text": "-242.12485388276099",
        "@units": "km"
    },
    "X_DOT": {
        "#text": "5.9511600325922904",
        "@units": "km/s"
    },
    "Y": {
        "#text": "-5285.0073157200604",
        "@units": "km"
    },
    "Y_DOT": {
        "#text": "-3.1998687127665399",
        "@units": "km/s"
    },
    "Z": {
        "#text": "4254.7035249005503",
        "@units": "km"
    },
    "Z_DOT": {
        "#text": "-3.6194381039437298",
        "@units": "km/s"
    }
    },...
```
</td>
</tr>
<tr>
<td> <code>/epochs</code> </td>
<td>

A list of all Epochs in the data set               

``` 
... "2023-063T11:31:00.000Z",   "2023-063T11:35:00.000Z",   "2023-063T11:39:00.000Z",   "2023-063T11:43:00.000Z",   "2023-063T11:47:00.000Z",   "2023-063T11:51:00.000Z",   "2023-063T11:55:00.000Z",   "2023-063T11:59:00.000Z",   "2023-063T12:00:00.000Z",...
```

</td>
</tr>

<tr>
<td> <code>/epochs/&ltepoch&gt </code> </td>
<td>

State vectors for a specific Epoch from the data set               

``` 
{
  "StateVector": {
    "X": {
      "#text": "2820.04422055639",
      "@units": "km"
    },
    "X_DOT": {
      "#text": "5.0375825820999403",
      "@units": "km/s"
    },
    "Y": {
      "#text": "-5957.89709645725",
      "@units": "km"
    },
    "Y_DOT": {
      "#text": "0.78494316057540003",
      "@units": "km/s"
    },
    "Z": {
      "#text": "1652.0698653803699",
      "@units": "km"
    },
    "Z_DOT": {
      "#text": "-5.7191913150960803",
      "@units": "km/s"
    }
  }
}
```
Instantaneous speed for a specific Epoch in the data set
</td>
</tr>

<tr>
<td> <code>/epochs/&ltepoch&gt/speed </code> </td>
<td>

Instantaneous speed for a specific Epoch in the data set               

``` 
{
  "Speed": {
    "#text": 7.661757196327827,
    "@units": "km/s"
  }
}
```

</td>
</tr>

<tr>
<td> <code>/help </code> </td>
<td>

Return help text that briefly describes each route

</td>
</tr>

<tr>
<td> <code>/delete-data </code> </td>
<td>

Delete all data from the dictionary object

</td>
</tr>

<tr>
<td> <code>/post-data </code> </td>
<td>

Reload the dictionary object with data from the web

</td>
</tr>

<tr>
<td> <code>/comment </code> </td>
<td>

Return ‘comment’ list obejct from ISS data

</td>
</tr>

<tr>
<td> <code>/header </code> </td>
<td>

Return ‘header’ dict object from ISS data

</td>
</tr>

<tr>
<td> <code>/metadata </code> </td>
<td>

Return ‘metadata’ dict object from ISS data

</td>
</tr>

<tr>
<td> <code>/epochs/&ltepoch&gt/location </code> </td>
<td>

Return latitude, longitude, altitude, and geoposition for given Epoch

</td>
</tr>

<tr>
<td> <code>/now </code> </td>
<td>

Return latitude, longitude, altidue, and geoposition for Epoch that is nearest in time

</td>
</tr>
</table>                                      

To access the other routes, append it to the command previously mentioned in [Make a Request](#make-a-request).