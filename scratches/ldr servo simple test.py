import time
import RPi.GPIO as GPIO
from adafruit_servokit import ServoKit

# Constants
TRIGGER_PINS = [21]  # Example GPIO pins
TRIGGER_EVENT = "RISING"  # Example event
SERVO_CHANNEL = 2  # The servo channel on the ServoKit

# Initialize ServoKit
kit = ServoKit(channels=16)

# Global variable to stop the servo rotation
stop_rotate = False

# Callback function for GPIO event
def set_stop_rotate(channel):
    global stop_rotate
    print(f"Trigger event detected on pin {channel}")
    stop_rotate = True

# Function to set up GPIO
def setup_gpio(trigger_pins, trigger_event):
    try:
        GPIO.setmode(GPIO.BCM)

        event_mapping = {
            "RISING": GPIO.RISING,
            "FALLING": GPIO.FALLING,
            "BOTH": GPIO.BOTH
        }

        if trigger_event not in event_mapping:
            raise ValueError(f"Invalid trigger_event: {trigger_event}")

        gpio_event = event_mapping[trigger_event]

        for pin in trigger_pins:
            GPIO.setup(pin, GPIO.IN)
            GPIO.add_event_detect(pin, gpio_event, callback=set_stop_rotate, bouncetime=50)

        print(f"GPIO setup complete with pins {trigger_pins} and event {trigger_event}")

    except Exception as e:
        try:
            GPIO.cleanup()
        except:
            pass
        print(f"An error occurred: {e}")
        print("GPIO setting failed")

# Function to control the servo motor
def control_servo():
    global stop_rotate
    print("Controlling servo...")
    while True:
        if stop_rotate:
            kit.servo[SERVO_CHANNEL].angle = 90
            print("Stopped Rotation")
            time.sleep(0.1)
            break
        else:
            kit.servo[SERVO_CHANNEL].angle = 0
            time.sleep(0.5)

# Main script execution
if __name__ == "__main__":
    try:
        # Setup GPIO
        setup_gpio(TRIGGER_PINS, TRIGGER_EVENT)
        
        # Control the servo motor based on GPIO events
        control_servo()
        
    finally:
        # Cleanup GPIO when done
        GPIO.cleanup()
