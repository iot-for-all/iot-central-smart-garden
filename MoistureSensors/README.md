# Instructions for setting up the Capacitive Moisture Sensors to work with Azure IoT
## You will need
<ul>
  <li> Capacitive Moisture Sensor v2 x 4 https://www.amazon.com/AITRIP-Capacitive-Corrosion-Resistant-Electronic/dp/B094J8XD83/ref=sr_1_14?dchild=1&keywords=capacitive+soil+moisture+sensor&qid=1624053466&sr=8-14</li>
  <li> Arduino board with four analog inputs (may need and analog extension board)</li>
  <li> Raspberry Pi</li>
  <li> USB A to USB B (or someway to serial connect your arduino to the raspberry pi)</li>
  <li> Wiring (Jumpers can work, but won't be as reliable as sodered wires when deployed) </li>
  <li> IoT Power Relay https://www.sparkfun.com/products/14236 </li>
  <li> Solinoid Value Hosing https://www.amazon.com/SparkFun-12V-Solenoid-Valve/dp/B007R9U9BM </li>
  <li> Some way to connect the relay to the valve (I used a Female DC Power Terminal https://www.cctvcameraworld.com/dc-female-power-terminal.html connected to a barrel jack cable with an outlet plug) </li>
</ul>

## Recommended supplies
<ul>
  <li> Electrical Waterproofing Coating (I used the silicon coating here https://www.amazon.com/MG-Chemicals-Silicone-Modified-Conformal/dp/B008O9YIV6/ref=sr_1_6?dchild=1&keywords=Silicone+Conformal+Coating&qid=1624059183&s=industrial&sr=1-6) </li>
  <li> Heat Shrink Tubing </li>
</ul> 

## Waterproofing your Sensors
It is a good idea to waterproof the moisture sensors electronic tops, especially if you plan to deploy them outdoors <br>
To do so start off by applying some sort of electrical waterproof coating only to the area above the line on the sensor, I used a silocon conformal coating linked above. If you plan to use the same productmake sure to apply at least three coats to ensure good waterproofing <br>

The three pins near the connector on the sensor are particularly sensitive, so I decided to lay it down rather thick around there (This is most likely unnessesary with the shrink tubing)<br>

Make sure to let it completely dry between coats, or it may end up looking someone gloopy and messy like mine did, but this will not affect the reading eitherway<br>

once you have everything the way you want it cover the electrical portion with a heat shrink tubing that fits and shrink it down to fit overtop

## Wiring
1. Start wiring connecting all four moisture sensors to the analog inputs on your ardiuno

## Code Setup
### Arduino Code
1. Start by making sure you have the arduino IDE installed, if not you can download it here: https://www.arduino.cc/en/software
2. Once installed run the IDE hit file and open the arduino file included in the repo
3. In tools make sure you have your board selected and that you are on the correct port
4. Verify and Upload the code to your arduino
5. you can check the output by checking the serial monitor under tools and you should see a JSON being sent across serial with sensor readings

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
device_id = ""
model_id = ""  
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
python MoistureSensorIOT.py
```
*or*
``` shell
python3 MoistureSensorIOT.py
``` 

## IOT Central Template
Included is a basic device template for this program <br>
To load it go to Device Templates in IOT Central, hit new -> IOT Device -> Next -> name it -> Next -> Create <br>
Then hit Import a Model and load the included moisture_sensors.json <br>
From here you are free to add your own views and forms using the incoming data

## Properties File

