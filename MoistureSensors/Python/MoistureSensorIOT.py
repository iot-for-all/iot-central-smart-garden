import asyncio
import base64
import hmac
import hashlib
import random
import serial
import json
import RPi.GPIO as GPIO

from azure.iot.device.aio import ProvisioningDeviceClient
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message
from azure.iot.device import MethodResponse
from azure.iot.device import exceptions

# property file
json_file =  open('Properties.txt')
prop = json.load(json_file)
json_file.close()

# device settings - FILL IN YOUR VALUES HERE
scope_id = "0ne002C0E3A"
group_symmetric_key = "d0T14jbEKvxZKC0HsKhktudbTlRLdm6W94oKqDrt1cD3H9Mu1JQ5uvF0XO/jwuT/tDIKZTWUze+TBGFV2rcJpg=="

# optional device settings - CHANGE IF DESIRED/NECESSARY
provisioning_host = "global.azure-devices-provisioning.net"
device_id = "moisture_sensor_rpi"
model_id = "dtmi:hollierHome:moisturesensors74j;1"  # 

# test setting flags
telemetry_send_on = True
reported_property_send_on = True
desired_property_receive_on = True
direct_method_receive_on = True
c2d_command_receive_on = True

# adjustable times and timeouts
await_timeout = 4.0
yield_time = 1.0
connection_monitor_sleep = 1.0
sendFrequency = prop["sendFrequency"]

# general purpose variables
use_websockets = True
device_client = None
terminate = False
trying_to_connect = False
max_connection_attempt = 3

# Pump variables
threshold = prop["threshold"]
waterRuntime = prop["waterRuntime"]
waitTime = prop["waitTime"]
openWater = False

# Calibration variables
min_fix = [prop["min1"], prop["min2"], prop["min3"], prop["min4"]]
max_fix = [prop["max1"], prop["max2"], prop["max3"], prop["max4"]]

# derives a symmetric device key for a device id using the group symmetric key
def derive_device_key(device_id, group_symmetric_key):
    message = device_id.encode("utf-8")
    signing_key = base64.b64decode(group_symmetric_key.encode("utf-8"))
    signed_hmac = hmac.HMAC(signing_key, message, hashlib.sha256)
    device_key_encoded = base64.b64encode(signed_hmac.digest())
    return device_key_encoded.decode("utf-8")

# modified arduino map() function, hard coded inputs to keep code consise, used to correct uncalibrated data. Code modified from https://www.arduino.cc/reference/en/language/functions/math/map/
def pMap(val, sensor):
    return int(round(val - min_fix[sensor]) * (100 - 0) / (max_fix[sensor] - min_fix[sensor]))

# coroutine that sends telemetry on a set frequency until terminated
async def send_telemetry():
    while not terminate:
        if device_client and device_client.connected:
            ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1) # Serial must be plugged or this will crash the program
            ser.flush()
            line = ser.readline().decode('utf-8').rstrip() # Grab Json String from Serial
            data = json.loads(line)
            payload = '{"sensorOne": %f, "sensorTwo": %f, "sensorThree": %f, "sensorFour": %f, "uncalibratedOne": %f, "uncalibratedTwo": %f, "uncalibratedThree": %f, "uncalibratedFour": %f}' % (pMap(data["sensorOne"], 0), pMap(data["sensorTwo"], 1), pMap(data["sensorThree"], 2), pMap(data["sensorFour"], 3), data["sensorOne"], data["sensorTwo"], data["sensorThree"], data["sensorFour"])
            print("sending message: %s" % (payload))
            msg = Message(payload)
            msg.content_type = "application/json"
            msg.content_encoding = "utf-8"
            if ((pMap(data["sensorOne"], 0) + pMap(data["sensorTwo"], 1) + pMap(data["sensorThree"], 2) + pMap(data["sensorFour"], 3)) / 4) <= threshold: # use pMap function to check if calibrated values average to be threshold or lower
                global openWater
                openWater = True # Trigger open value function to release water
            try:
                await asyncio.wait_for(device_client.send_message(msg), timeout=await_timeout)
                print("completed sending message")
            except asyncio.TimeoutError:
                continue
            await asyncio.sleep(sendFrequency)  # sleep until it's time to send again
        else:
            await asyncio.sleep(yield_time)  # do this to yield the busy loop or you will block all other tasks

# coroutine to open the valve for releasing the water
async def open_valve():
    while not terminate:
        global openWater 
        if openWater: # loops til openWater is triggered in sendTelemetry
            GPIO_PIN = 17 # pin can be changed if a different pin is used in wiring
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(GPIO_PIN, GPIO.OUT)
            GPIO.output(GPIO_PIN, GPIO.HIGH) # open valve
            await asyncio.sleep(waterRuntime) # sleep until its time to shut the value off
            GPIO.output(GPIO_PIN, GPIO.LOW) # close value
            await asyncio.sleep(waitTime) # sleep for waittime
            openWater = False


# coroutine that sends reported properties on a set frequency until terminated
async def send_reportedProperty():
    while not terminate:
        if device_client and device_client.connected:
            reported_payload = {"sendFrequency": sendFrequency}
            print("Sending reported property: {}".format(reported_payload))
            try:
                await asyncio.wait_for(device_client.patch_twin_reported_properties(reported_payload), timeout=await_timeout)
            except asyncio.TimeoutError:
                continue
            await asyncio.sleep(15)  # sleep until it's time to send again
        else:
            await asyncio.sleep(yield_time) # do this to yield the busy loop or you will block all other tasks



# handles desired properties from IoT Central (or hub) until terminated
async def desired_property_handler(patch):
    global prop
    print("Desired property received, the data in the desired properties patch is: {}".format(patch))
    # acknowledge the desired property back to IoT Central
    for key in list(patch.keys()):
        if key == "sendFrequency":
            global sendFrequency
            sendFrequency = patch[key]
            prop["sendFrequency"] = sendFrequency
        if key == "wateringParameters": # watering values
            global waterRuntime, waitTime, threshold
            waterRuntime = patch[key]["waterRuntime"]
            prop["waterRuntime"] = waterRuntime
            waitTime = patch[key]["waitTime"]
            prop["waitTime"] = waitTime
            threshold = patch[key]["threshold"]
            prop["threshold"] = threshold
        if key == "calibrate": # calibration values
            global min_fix, max_fix
            min_fix = [patch[key]["minFix"]["one"], patch[key]["minFix"]["two"], patch[key]["minFix"]["three"], patch[key]["minFix"]["four"]]
            prop["min1"] = min_fix[0]
            prop["min2"] = min_fix[1]
            prop["min3"] = min_fix[2]
            prop["min4"] = min_fix[3]
            max_fix = [patch[key]["maxFix"]["one"], patch[key]["maxFix"]["two"], patch[key]["maxFix"]["three"], patch[key]["maxFix"]["four"]]
            prop["max1"] = max_fix[0]
            prop["max2"] = max_fix[1]
            prop["max3"] = max_fix[2]
            prop["max4"] = max_fix[3]
        if key != "$version":
            reported_payload = {key:{"value": patch[key], "ac":200, "ad":"completed", "av":patch['$version']}}
            await asyncio.wait_for(device_client.patch_twin_reported_properties(reported_payload), timeout=await_timeout)
            print(reported_payload)
        
        with open('Properties.txt', 'w') as outfile: # writes new values to properties file
            json.dump(prop, outfile)


# handles direct methods from IoT Central (or hub) until terminated
async def direct_method_handler(method_request):
    print("executing direct method: %s(%s)" % (method_request.name, method_request.payload))
    method_response = None
    if method_request.name == "echo":
        # send response - echo back the payload
        method_response = MethodResponse.create_from_method_request(method_request, 200, method_request.payload)
    else:
        # send bad request status code
        method_response = MethodResponse.create_from_method_request(method_request, 400, "unknown command")
    await asyncio.wait_for(device_client.send_method_response(method_response), timeout=await_timeout)
        

# coroutine to monitor the connection to see if we need to reconnect
async def monitor_connection():
    global device_client, terminate

    while not terminate:
        if not trying_to_connect and not device_client.connected:
            device_client = None
            if not await connect():
                print('Cannot connect to Azure IoT Central please check the application settings and machine connectivity')
                print('Terminating all running tasks and exiting ...')
                terminate = True
        await asyncio.sleep(connection_monitor_sleep)


# connect is not optimized for caching the IoT Hub hostname so all connects go through Device Provisioning Service (DPS)
# a strategy here would be to try just the hub connection using a cached IoT Hub hostname and if that fails fall back to a full DPS connect
async def connect():
    global device_client

    trying_to_connect = True
    device_symmetric_key = derive_device_key(device_id, group_symmetric_key)

    connection_attempt_count = 0
    connected = False
    while not connected and connection_attempt_count < max_connection_attempt:
        provisioning_device_client = ProvisioningDeviceClient.create_from_symmetric_key(
            provisioning_host=provisioning_host,
            registration_id=device_id,
            id_scope=scope_id,
            symmetric_key=device_symmetric_key,
            websockets=use_websockets
        )

        provisioning_device_client.provisioning_payload = '{"iotcModelId":"%s"}' % (model_id)
        registration_result = None

        try:
            registration_result = await provisioning_device_client.register()
        except (exceptions.CredentialError, exceptions.ConnectionFailedError, exceptions.ConnectionDroppedError, exceptions.ClientError, Exception) as e:
            print("DPS registration exception: " + e)
            connection_attempt_count += 1

        if registration_result.status == "assigned":
            dps_registered = True

        if dps_registered:
            device_client = IoTHubDeviceClient.create_from_symmetric_key(
                symmetric_key=device_symmetric_key,
                hostname=registration_result.registration_state.assigned_hub,
                device_id=registration_result.registration_state.device_id,
                websockets=use_websockets
            )

        try:
            device_client.on_twin_desired_properties_patch_received = desired_property_handler
            device_client.on_method_request_received = direct_method_handler

            await device_client.connect()
            trying_to_connect = False
            connected = True



        except Exception as e:
            print("Connection failed, retry %d of %d" % (connection_attempt_count, max_connection_attempt))
            connection_attempt_count += 1

    return connected


async def main():
    random.seed()

    if await connect():
        # start the tasks if the task flag is set to on
        tasks = []
        tasks.append(asyncio.create_task(send_telemetry())) # send telemetry
        tasks.append(asyncio.create_task(open_valve())) # listen for the valve to open
        tasks.append(asyncio.create_task(send_reportedProperty())) # send reported property
        tasks.append(asyncio.create_task(monitor_connection()))  # task to monitor for disconnects and perform reconnect

        #await the tasks ending before exiting
        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            pass # ignore the cancel actions on twin_listener and direct_method_listener

        # finally, disconnect
        print("Disconnecting from IoT Hub")
        await device_client.disconnect()
    else:
        print('Cannot connect to Azure IoT Central please check the application settings and machine connectivity')

# start the main routine
if __name__ == "__main__":
    loop = asyncio.run(main())

    # If using Python 3.6 or below, use the following code instead of asyncio.run(main()):
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.close()