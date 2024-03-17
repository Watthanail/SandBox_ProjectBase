#include <Arduino.h>
#include "ModbusMaster.h"
#define LED01 32
#define PROXY 34
#define MAX485_DE 5
#define MAX485_RE_NEG 4
ModbusMaster node;
// Define a structure to hold RS485 data
struct RS485Data {
  uint16_t result;
  uint16_t distance;
};

// Global instance of the RS485Data structure
RS485Data rs485Data;
bool led01 = 0;


void preTransmission()
{
  digitalWrite(MAX485_RE_NEG, 1);
  digitalWrite(MAX485_DE, 1);
}
void postTransmission()
{
  digitalWrite(MAX485_RE_NEG, 0);
  digitalWrite(MAX485_DE, 0);
}

void setup()
{
  Serial.begin(115200);
  pinMode(MAX485_RE_NEG, OUTPUT);
  pinMode(MAX485_DE, OUTPUT);
  pinMode(PROXY, INPUT);
  pinMode(LED01, OUTPUT);
  digitalWrite(MAX485_RE_NEG, 0);
  digitalWrite(MAX485_DE, 0);

  Serial2.begin(115200);
  while (!Serial2)
  {
    Serial.println("loop for init software serial");
  }
  node.begin(128, Serial2); // Address
  node.preTransmission(preTransmission);
  node.postTransmission(postTransmission);
}

void loop()
{
  bool Detection = digitalRead(PROXY);
  rs485Data.result = node.readHoldingRegisters(0x9C7D, 1);

  if (rs485Data.result == node.ku8MBSuccess)
  {
    // Serial.print("Response Data: ");
    // for (int i = 0; i < 2; i++) // Assuming the response buffer length is 2 bytes
    // {
    //   Serial.print(node.getResponseBuffer(i));
    //   Serial.print(" ");
    // }
    rs485Data.distance = node.getResponseBuffer(0);
    Serial.printf("Distance_RS485: %d mm. Detection: %d \n", rs485Data.distance, Detection);

    if (Detection == 0)
    {
      led01 = 1;
      digitalWrite(LED01, led01);
    }
    else
    {
      led01 = 0;
      digitalWrite(LED01, led01);
    }
  }
}