#define BLYNK_PRINT Serial


#define BLYNK_TEMPLATE_ID ""TMPL3PnUkvitc""
#define BLYNK_TEMPLATE_NAME ""Pet Feeder""
#define BLYNK_AUTH_TOKEN "LIcWrFjQoTDRT8XAj6ZQ3TL5hm8vxnnN "


#include <ESP8266WiFi.h>
#include <BlynkSimpleEsp8266.h>
#include <Servo.h>
#include <TimeLib.h>
#include <WidgetRTC.h>


char ssid[] = "realmec3";
char pass[] = "ragini@123";


Servo feederServo;
WidgetRTC rtc;


int servoPin = D1;
int feedCount = 0;
String feedHistory = "None";


// Manual feed button
BLYNK_WRITE(V0) {
  if (param.asInt() == 1) {
    feedPet();
  }
}


// Sync values when ESP connects
BLYNK_CONNECTED() {
  rtc.begin();
}




void feedPet() {
  Blynk.virtualWrite(V2, "Feeding Started");


  feederServo.write(90);
  delay(2000);
  feederServo.write(0);


  // Update feeding count
  feedCount=feedCount+1;
  Blynk.virtualWrite(V1, feedCount);


  // Get current time
  String currentTime = String(hour()) + ":" +
                       (minute() < 10 ? "0" : "") + String(minute());


  


  Blynk.virtualWrite(V3, feedHistory);
  Blynk.virtualWrite(V2, "✅ Food Dispensed Successfully");
}


void setup() {
  Serial.begin(9600);


  feederServo.attach(servoPin);
  feederServo.write(0);


  Blynk.begin(BLYNK_AUTH_TOKEN, ssid, pass);
}


void loop() {
  Blynk.run();
}
