#include <ArduinoJson.h>

const int capacity = JSON_OBJECT_SIZE(4);

void setup() {
  Serial.begin(9600);
  while (!Serial) continue;
}

void loop() { 
  int sensorVal[4] = {analogRead(A0), analogRead(A1), analogRead(A2), analogRead(A3)};
  int percentageHumididy[4] = {map(sensorVal[0], 260, 620, 100, 0), map(sensorVal[1], 260, 620, 100, 0), map(sensorVal[2], 260, 620, 100, 0), map(sensorVal[3], 260, 620, 100, 0),};
  

  StaticJsonDocument<capacity> doc;
  doc["sensorOne"] = percentageHumididy[0];
  doc["sensorTwo"] = percentageHumididy[1];
  doc["sensorThree"] = percentageHumididy[2];
  doc["sensorFour"] = percentageHumididy[3];
  serializeJson(doc, Serial);

  Serial.println();
  
  delay(1000);
}
