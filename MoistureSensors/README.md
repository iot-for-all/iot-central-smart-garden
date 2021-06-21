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
  <li> A container deep enough to submerge sensor </li>
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
1. Start wiring by connecting all four moisture sensors to the analog inputs on your ardiuno
  - Connect AOUT on the sensor to analog 0 - 3
  - Connect VCC on sensor to 5V
  - Connect GND on sensor to GND

![image](https://user-images.githubusercontent.com/59976596/122829358-c2821180-d29b-11eb-9ea5-3defc3527353.png)

2. Next use your USB B to USB A to serial connect your Arduino to the Raspberry Pi

![image](https://user-images.githubusercontent.com/59976596/122829848-5d7aeb80-d29c-11eb-8ecb-eea9af00bd73.png)

3. Connect wires to GPIO pins 9 (GND) and 11 (GPIO 17), then connect these wires to the relay with 9 to Negative and 11 to Positive

![image](https://user-images.githubusercontent.com/59976596/122832538-5950cd00-d2a0-11eb-9bf4-a4fa1a203821.png) <br>
(Red - pin 11, Brown - pin 9)

4. Plug in the valve to normally off by connecting a plug to a valve

![image](https://user-images.githubusercontent.com/59976596/122833043-265b0900-d2a1-11eb-9855-05e5d423de88.png)

5. Plug in the relay and the Raspberry Pi and your wiring is complete

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
device_id = "moisture_sensor_rpi"
model_id = "dtmi:sample:moisturesensors;1"  
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

## Calibration
Since the sensors are all a bit different, each sensor will have to be calibrated separately. You can do this either through IOT or the property file. For each sensor you will need to find the minimum value and the maximum value.
1. Start by running the IOT program in order to see the values of the sensors
2. One by one pick the dry sensors up by the top avoiding any connections
3. Write down the uncalibrated value for each sensor
4. Next take a container of water that you can submerge your sensor in and one by one submerge your sensors to the white line
5. Let the sensor sit submerged until the uncalibrated value stops changing, when it does write down that value
6. Now with the dry and wet values for the sensors, use them to fill out either the min and max values in the property file, or the calibrate property on IOT Central using forms

## Properties File
For the moisture sensors there are twelve editable properties in the property file. <br>
In order, they are:
<ul>
  <li> sendFrequency: How often telemetry is sent to IOT Central </li>
  <li> threshold: Threshold average value for opening the valve </li>
  <li> waterRuntime: How long the valve stays open </li>
  <li> waitTime: Time after the valve closes before it can be opened again, allows the sensors time to adjust </li>
  <li> min1 - 4: Lower bounds for calibration </li>
  <li> max1 - 4: Upper bounds for calibration </li>
</ul>

These properties are directly editable from the properties file, or through a form on IOT Central
