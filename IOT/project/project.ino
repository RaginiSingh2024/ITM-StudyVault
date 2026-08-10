#define BLYNK_TEMPLATE_ID ""
#define BLYNK_TEMPLATE_NAME "NoiseAlert"
#define BLYNK_AUTH_TOKEN ""

#include <ESP8266WiFi.h>
#include <BlynkSimpleEsp8266.h>

char ssid[] = "Your wifi name";
char pass[] = "your wifi password";

#define SOUND A0
#define BUZZER D1
#define LED D2

int threshold = 300;
bool alertSent = false;

void setup()
{
  Serial.begin(9600);

  pinMode(BUZZER, OUTPUT);
  pinMode(LED, OUTPUT);

  digitalWrite(BUZZER, LOW);
  digitalWrite(LED, LOW);

  Blynk.begin(BLYNK_AUTH_TOKEN, ssid, pass);
}

void loop()
{
  Blynk.run();

  int value = analogRead(SOUND);
  Serial.println(value);

  Blynk.virtualWrite(V0, value);

  if(value > threshold)
  {
    digitalWrite(BUZZER, HIGH);
    digitalWrite(LED, HIGH);
    Blynk.virtualWrite(V1, "Noise Detected");
  }
  else
  {
    digitalWrite(BUZZER, LOW);
    digitalWrite(LED, LOW);
    Blynk.virtualWrite(V1, "System Normal");
  }

  delay(20);
}