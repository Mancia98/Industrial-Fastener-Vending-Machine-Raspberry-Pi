// SOFTWARE_NAME = vending machine_coinslot MCU program
// CODE_VERSION =2.0
// PLATFORM = ARDUINO


#include <Servo.h>

// Pin definitions
const int PIN_IN = 11;

// State variables
int switchState = 0;
int prevState = HIGH;
int pulseCount = 0;

// Timing variables
const unsigned long MaxElapsedTime = 500; // Maximum elapsed time to consider pulses part of the same coin insertion
unsigned long startTime = 0;              // Start time for pulse counting

// Servo objects
Servo servo1;
Servo servo2;
Servo servo3;

// Function to initialize servos
void setupServos() {
  servo1.attach(8);
  servo2.attach(9);
  servo3.attach(10);
}

// Function to process user input and dispense coins
void processUserInput(String userInput) {
  int pos = 0;
  int numCoins = 0;
  int denomination = 0;

  // Parse the input string
  while ((pos = userInput.indexOf(',')) != -1) {
    String token = userInput.substring(0, pos); // Extract token until comma
    userInput.remove(0, pos + 1); // Remove processed token from input string

    // Extract denomination and quantity
    int colonPos = token.indexOf(':');
    denomination = token.substring(0, colonPos).toInt();
    numCoins = token.substring(colonPos + 1).toInt();

    // Dispense coins
    if (denomination == 10) {
      dispenseCoins(servo1, numCoins);
    } else if (denomination == 5) {
      dispenseCoins(servo2, numCoins);
    } else if (denomination == 1) {
      dispenseCoins(servo3, numCoins);
    }
  }

  // Process the last token (no comma after the last token)
  int colonPos = userInput.indexOf(':');
  denomination = userInput.substring(0, colonPos).toInt();
  numCoins = userInput.substring(colonPos + 1).toInt();
  if (denomination == 10) {
    dispenseCoins(servo1, numCoins);
  } else if (denomination == 5) {
    dispenseCoins(servo2, numCoins);
  } else if (denomination == 1) {
    dispenseCoins(servo3, numCoins);
  }
}

// Function to dispense coins using servo
void dispenseCoins(Servo& servo, int numCoins) {
  for (int i = 0; i < numCoins; i++) {
    servo.write(0);
    delay(500);
    servo.write(125);
    delay(500);
  }
  Serial.print("CHANGE:");
  Serial.println("DONE");
}

void setup() {
  // Initialize serial communication at 9600 baud
  Serial.begin(9600);
  Serial.println("Coin Dispenser Ready");
  
  // Attach servos to pins
  setupServos();
}

void loop() {
  // Read the state of the input pin
  switchState = digitalRead(PIN_IN);

  // Detect falling edge of the input signal
  if (switchState == LOW && prevState == HIGH) {
    pulseCount++;
    startTime = millis(); // Reset the start time
  } else {
    // Calculate elapsed time since the last pulse
    unsigned long currentTime = millis();
    unsigned long elapsedTime = currentTime - startTime;

    // Check if the elapsed time exceeds the maximum allowed time
    if (elapsedTime > MaxElapsedTime && pulseCount > 0) {
      // Print the number of coins received
      Serial.print("COINS:");
      Serial.println(pulseCount);
      
      // Reset pulse count and start time
      pulseCount = 0;
      startTime = millis();
    }
  }

  // Update the previous state of the input pin
  prevState = switchState;

  // Check if there is any serial input
  if (Serial.available() > 0) {
    String userInput = Serial.readStringUntil('\n'); // Read the entire input line
    userInput.trim(); // Remove leading/trailing whitespace

    // Process user input to dispense coins
    processUserInput(userInput);
  }
}
