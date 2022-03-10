// Script for the ArtButton
// 09.03.2022
// Lucas Wirz-Vitiuk

// Include libraries
#include <BleKeyboard.h>
BleKeyboard bleKeyboard("Art Button");

// Pin definitions
const int buttonPin = 23;
const int shutdownPin = 21;

// Pin-State variable
boolean oldPin1State = LOW;
boolean oldPin2State = LOW;

void setup() {
  //Start the Serial communication
  Serial.begin(115200);
  Serial.println("Art Button started");

  //Initiate bluetooth keyboard
  bleKeyboard.begin();

  //Initiate Pins
  pinMode(buttonPin, INPUT_PULLDOWN);
  pinMode(shutdownPin, INPUT_PULLDOWN);
}

void loop() {
  if (bleKeyboard.isConnected()) {

    // Define the Art Button as spacebar
    if (digitalRead(buttonPin) == HIGH) {
      if (oldPin1State == LOW) {
        bleKeyboard.print(" ");
      }
      oldPin1State = HIGH;
    } else {
      oldPin1State = LOW;
    }

    // Define shutdown button as 'E'
    if (digitalRead(shutdownPin) == HIGH) {
      if (oldPin2State == LOW) {
        bleKeyboard.print("E");
      }
      oldPin2State = HIGH;
    } else {
      oldPin2State = LOW;
    }
  }
  delay(50);
}
