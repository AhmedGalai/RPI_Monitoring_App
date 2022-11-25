#include <Adafruit_Sensor.h> //Library for Adafruit sensors , we are using for DHT
#include <DHT_U.h> //DHT library which uses some func from Adafruit Sensor library
#include <ESP8266WiFi.h> //library for using ESP8266 WiFi 
#include <PubSubClient.h> //library for MQTT
#include <ArduinoJson.h> //library for Parsing JSON
#include "time.h"
//defining Pins
#define DHTPIN 5
#define LICHT D2
#define VENTIL 3
#define VERNEBLER 10
 
//DHT parameters
#define DHTTYPE    DHT11     // DHT 11
DHT_Unified dht(DHTPIN, DHTTYPE);
uint32_t delayMS;
 
//MQTT Credentials
const char* ssid = "FRITZ!Box 7530 PQ";//setting your ap ssid
const char* password = "41120895611457227941";//setting your ap psk
const char* mqttServer = "iot.reyax.com"; //MQTT URL
const char* mqttUserName = "mqtt username";  // MQTT username
const char* mqttPwd = "mqtt password";  // MQTT password
const char* clientID = "username0001"; // client id username+0001
const char* topic = "Messung"; //publish topic
 
//parameters for using non-blocking delay
unsigned long previousMillis = 0;
const long interval = 5000;
const long  gmtOffset_sec = 0;
const int   daylightOffset_sec = 3600;


String msgStr = "";      // MQTT message buffer
 
float temp, hum;
 
 
//setting up wifi and mqtt client
WiFiClient espClient;
PubSubClient client(espClient);
 
void setup_wifi() {
  delay(10);
 
  WiFi.begin(ssid, password);
 
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
 
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
 
}
 
void reconnect() {
  while (!client.connected()) {
    if (client.connect(clientID, mqttUserName, mqttPwd)) {
      Serial.println("MQTT connected");
 
      client.subscribe("Steuerung");
      Serial.println("Topic Subscribed");
    }
    else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);  // wait 5sec and retry
    }
 
  }
 
}

void autoLicht() {
  if (timeHour == '22') {
    digitalWrite(LICHT, 1);
  } else {
    digitalWrite(LICHT, 0);
  }
}

void autoVernebler() {
  if (hum > 90) {
    digitalWrite(VERNEBLER, 0);
  } else {
    digitalWrite(VERNEBLER, 1);
  }
}

void autoVentil() {
  if (hum > 90) {
    digitalWrite(VERNEBLER, 1);
  } else {
    digitalWrite(VERNEBLER, 0);
  }
}
 
//subscribe call back
void callback(char*topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived in topic: ");
  Serial.println(topic);
  Serial.print("Message:");
  String data = "";
  for (int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
    data += (char)payload[i];
  }
  Serial.println();
  Serial.print("Message size :");
  Serial.println(length);
  Serial.println();
  Serial.println("-----------------------");
  Serial.println(data);
 
switch(data=="1"){
  case '1' : {
    Serial.println("VERNEBLER_AUTO");
    autoVernebler();
  }
  case '2' : {
    Serial.println("VERNEBLER_AN");
    digitalWrite(VERNEBLER, 1);
  }
  case '3' : {
    Serial.println("VERNEBLER_AUS");
    digitalWrite(VERNEBLER, 0);
  }
  case '4' : {
    Serial.println("VENTIL_AUTO");
    autoVentil();
  }
  case '5' : {
    Serial.println("VENTIL_AN");
    digitalWrite(VENTIL, 1);
  }
  case '6' : {
    Serial.println("VENTIL_AUS");
    digitalWrite(VENTIL, 0);
  }
  case '7' : {
    Serial.println("LICHT_AUTO");
    autoLicht();
  }
  case '8' : {
    Serial.println("LICHT_AN");
    digitalWrite(LICHT, 1);
  }
  case '9' : {
    Serial.println("LICHT_AUS");
    digitalWrite(LICHT, 0);
  }
  
}
 
 
void setup() {
  Serial.begin(115200);
  // Initialize device.
  dht.begin();
  // get temperature sensor details.
  sensor_t sensor;
  dht.temperature().getSensor(&sensor);
  dht.humidity().getSensor(&sensor);
 
  pinMode(LICHT, OUTPUT);
  digitalWrite(LICHT, LOW);
  pinMode(VERNEBLER, OUTPUT);
  digitalWrite(VERNEBLER, LOW);
  pinMode(VENTIL, OUTPUT);
  digitalWrite(VENTIL, LOW);
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
 
  setup_wifi();
 
  client.setServer(mqttServer, 1883); //setting MQTT server
  client.setCallback(callback); //defining function which will be called when message is received.
 
}
 
void loop() {
  struct tm timeinfo;
    if(!getLocalTime(&timeinfo)){
      Serial.println("Failed to obtain time");
      return;
    }
  char timeHour[3];
    strftime(timeHour,3, "%H", &timeinfo); 
  
  if (!client.connected()) { //if client is not connected
    reconnect(); //try to reconnect
  }
  client.loop();
 
  unsigned long currentMillis = millis(); //read current time
 
  if (currentMillis - previousMillis >= interval) { //if current time - last time > 5 sec
    previousMillis = currentMillis;
 
    //read temp and humidity
    sensors_event_t event;
    dht.temperature().getEvent(&event);
 
 
    if (isnan(event.temperature)) {
      Serial.println(F("Error reading temperature!"));
    }
    else {
      Serial.print(F("Temperature: "));
      temp = event.temperature;
      Serial.print(temp);
      Serial.println(F("xC"));
    }
    // Get humidity event and print its value.
    dht.humidity().getEvent(&event);
    if (isnan(event.relative_humidity)) {
      Serial.println(F("Error reading humidity!"));
    }
    else {
      Serial.print(F("Humidity: "));
      hum = event.relative_humidity;
      Serial.print(hum);
      Serial.println(F("%"));
    }
 
 
    msgStr = String(temp) +","+String(hum);
    byte arrSize = msgStr.length() + 1;
    char msg[arrSize];
 
    Serial.print("PUBLISH DATA:");
    Serial.println(msgStr);
    msgStr.toCharArray(msg, arrSize);
    client.publish(topic, msg);
    msgStr = "";
    delay(50);
 
  }
 
}
