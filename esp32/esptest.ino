/*********
  Rui Santos
  Complete project details at https://randomnerdtutorials.com  
*********/

// Import required libraries
#include "WiFi.h"
#include "ESPAsyncWebServer.h"
#include <Adafruit_Sensor.h>
#include <DHT.h>

// Replace with your network credentials
const char* ssid = "FRITZ!Box 7530 PQ";
const char* password = "41120895611457227941";

#define DHTPIN 26     // Digital pin connected to the DHT sensor
#define VENTIL 27
#define VERNEBLER 14
#define LICHT 12

// Uncomment the type of sensor in use:
#define DHTTYPE    DHT11     // DHT 11
//#define DHTTYPE    DHT22     // DHT 22 (AM2302)
//#define DHTTYPE    DHT21     // DHT 21 (AM2301)
const char* ntpServer = "pool.ntp.org";
const long  gmtOffset_sec = 0;
const int   daylightOffset_sec = 3600;
DHT dht(DHTPIN, DHTTYPE);
float tem, hum;
int vernebler_auto = 1;
int licht_auto = 1;
int ventil_auto = 1;
char timeHour[3];

// Create AsyncWebServer object on port 80
AsyncWebServer server(80);

String readDHTTemperature() {
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  // Read temperature as Celsius (the default)
  float t = dht.readTemperature();
  // Read temperature as Fahrenheit (isFahrenheit = true)
  //float t = dht.readTemperature(true);
  // Check if any reads failed and exit early (to try again).
  if (isnan(t)) {    
    Serial.println("Failed to read from DHT sensor!");
    return "--";
  }
  else {
    //Serial.println(t);
    return String(t);
  }
}

String readDHTHumidity() {
  // Sensor readings may also be up to 2 seconds 'old' (its a very slow sensor)
  float h = dht.readHumidity();
  if (isnan(h)) {
    Serial.println("Failed to read from DHT sensor!");
    return "--";
  }
  else {
    //Serial.println(h);
    return String(h);
  }
}


void autoLicht() {
  if (timeHour == "22") {
    digitalWrite(LICHT, 1);
  } else {
    digitalWrite(LICHT, 0);
  }
}

void autoVernebler() {
  if (hum > 89) {
    digitalWrite(VERNEBLER, 0);
  } else {
    digitalWrite(VERNEBLER, 1);
  }
}

void autoVentil() {
  if (hum > 91) {
    digitalWrite(VENTIL, 1);
  } else {
    digitalWrite(VENTIL, 0);
  }
}

String tempdata(){
    return readDHTTemperature()+','+readDHTHumidity();
}

void setup(){
  // Serial port for debugging purposes
  Serial.begin(115200);
  pinMode(VENTIL,OUTPUT);
  digitalWrite(VENTIL,0);
  pinMode(VERNEBLER,OUTPUT);
  digitalWrite(VERNEBLER,0);
  pinMode(LICHT,OUTPUT);
  digitalWrite(LICHT,0);
  dht.begin();
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);
  // Connect to Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi..");
  }

  // Print ESP32 Local IP Address
  Serial.println(WiFi.localIP());

  // Route for root / web page
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
    Serial.println("Messung:");
    Serial.println(tempdata().c_str());
    request->send_P(200, "text/plain", tempdata().c_str());
  });
  server.on("/1", HTTP_GET, [](AsyncWebServerRequest *request){
    Serial.println("Steuerung: 1");
    autoVernebler();
    vernebler_auto = 1;
  });
  server.on("/2", HTTP_GET, [](AsyncWebServerRequest *request){
    Serial.println("Steuerung: 2");
    digitalWrite(VERNEBLER,1);
    vernebler_auto = 0;
  });
  server.on("/3", HTTP_GET, [](AsyncWebServerRequest *request){
    Serial.println("Steuerung: 3");
    digitalWrite(VERNEBLER,0);
    vernebler_auto = 0;
  });
  server.on("/4", HTTP_GET, [](AsyncWebServerRequest *request){
    Serial.println("Steuerung: 4");
    autoVentil();
    ventil_auto = 1;
  });
  server.on("/5", HTTP_GET, [](AsyncWebServerRequest *request){
    Serial.println("Steuerung: 5");
    digitalWrite(VENTIL,1);
    ventil_auto = 0;
  });
  server.on("/6", HTTP_GET, [](AsyncWebServerRequest *request){
    Serial.println("Steuerung: 6");
    digitalWrite(VENTIL,0);
    ventil_auto = 0;
  });
  server.on("/7", HTTP_GET, [](AsyncWebServerRequest *request){
    Serial.println("Steuerung: 7");
    autoLicht();
    licht_auto = 1;
  });
  server.on("/8", HTTP_GET, [](AsyncWebServerRequest *request){
    Serial.println("Steuerung: 8");
    digitalWrite(LICHT,1);
    licht_auto = 0;
  });
  server.on("/9", HTTP_GET, [](AsyncWebServerRequest *request){
    Serial.println("Steuerung: 9");
    digitalWrite(LICHT,0);
    licht_auto = 0;
  });
  // Start server
  server.begin();
}
 
void loop(){
  struct tm timeinfo;
    if(!getLocalTime(&timeinfo)){
      Serial.println("Failed to obtain time");
      return;
    }
  char timeHour[3];
    strftime(timeHour,3, "%H", &timeinfo); 
  tem = dht.readTemperature();
  hum = dht.readHumidity();
  if (licht_auto) {
    autoLicht();
  }
  if (ventil_auto) {
    autoVentil();
  }
  if (vernebler_auto) {
    autoVernebler();
  }
 /*if (readDHTHumidity().toInt()>70){
   digitalWrite(Ventil,1);
 } else if (readDHTHumidity().toInt()<60){
   digitalWrite(Ventil,0);
 }*/
  delay(1000);
}