# Instructions for setting up the Micro: Climate kit to work with Azure IoT
## You will need
<ul>
  <li> Micro: Climate Kit </li>
  <li> Micro: Bit (Not included with Climate Kit)</li>
  <li> Raspberry Pi</li>
  <li> USB to USB micro cable (or someway to serial connect your micro:bit to the raspberry pi)</li>
</ul> 

Be sure to assemble your Micro: Climate Kit before starting, for instructions on assembly follow Sparkfun's assembly guide here: https://learn.sparkfun.com/tutorials/weather-meter-hookup-guide

## Wiring
With your Climate Kit assembled following the guide in the previous section, the wiring for this project becomes very simple<br>
<ul>
  <li> Simply plug the two wires from the climate kit into the appropiatly marked RAIN and WIND Sockets on the Weather:Bit and slot your micro:bit into the slot on the top. </li>
  <li> From there take your USB to micro USB and plug the micro end into the micro:bit and the USB end into the Raspberry Pi </li>
  <li> Plugging the battery pack into the micro:bit is optional, but unnessecary as the Raspberry Pi will power it </li>
  <li> Once you plug in your Raspberry Pi everything is set up and ready to run the code. </li>
</ul>

## Code Setup
### Micro:Bit Code
To setup the micro:bit just plug it into a machine, find the micro:bit directory and place the micro:bit hex file in the directory <br>
The Micro:bit should automatically upload the code and begin running it
### Python Code
1. Change the following code to add in your scope id and group SAS key. Both can be found in the Administration -> Device connection page.

``` Python
# device settings - FILL IN YOUR VALUES HERE
scope_id = ""
group_symmetric_key = ""
```

2. You can also optionally change the following options as well

``` Python
# optional device settings - CHANGE IF DESIRED/NECESSARY
provisioning_host = "global.azure-devices-provisioning.net"
device_id = "weather_station_rpi"
model_id = "dtmi:sample:weatherstation;1"  
```
3. This program requires Python 3.7+ to run check your version using
``` shell
python --version
```
*or*
``` shell
python3 --version
```
4. Install the nessesary libraries with pip
``` shell
pip install asyncio
pip install azure-iot-device
```
5. Finally once everything is properly hooked up, run the program by using the follow command in the directory with the code
``` shell
python WeatherStationIOT.py
```
*or*
``` shell
python3 WeatherStationIOT.py
``` 

## IOT Central Template
Included is a basic device template for this program <br>
To load it go to Device Templates in IOT Central, hit new -> IOT Device -> Next -> name it -> Next -> Create <br>
Then hit Import a Model and load the included weather_station.json <br>
From here you are free to add your own views and forms using the incoming data

## Properties File
Unlike the Moisture Sensor properties file, This one has only a single option, being the sendFrequency option, which determines the length between telemetry sends, 
feel free to edit this either directly from the file or through a form on IOT Central, it is writable on the template!

## Unused Climate Kit Features
The Micro:Climate Kit includes two sensors unused in this project
<ul>
  <li> Soil Moisture </li>
  <li> Soil Temperature </li>
</ul>

These aren't included in the code due to the repetitiveness with the moisture sensor part of this repo, however they wouldn't be very hard to hook up and add to the code, so I may add it eventually as an option.

## Altitude Sensor
Since the Altitude sensor on the Weather:bit uses pressure to gauge altitude, it may be inaccurate depending on the pressure and how it is deployed
