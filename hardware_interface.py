import serial
import time
data = ""


class Servo_Control():
    def __init__(self) -> None:
        self.is_connected = False
        self.index = 0
        self.__mode = "timed"
        self.__stop_rotate = False
        self.set_mode()

    def start_connection(self) -> bool:
        try:
            from adafruit_servokit import ServoKit
            self.kit = ServoKit(channels=16)
            self.is_connected = True
            print("ServoKit OK")
        except:
            from dummy_servokit import ServoKit
            print("ServoKit Failed")
        return self.is_connected

    def set_mode(self, mode: str = "timed", trigger_pins: list = None, trigger_event: str = "RISING"):
        if mode == "triggered":
            try:
                if trigger_pins is None:
                    raise ValueError("The trigger_pins cannot be None")

                if not isinstance(trigger_pins, list):
                    raise TypeError("The trigger_pins must be a list of integers")

                for pin in trigger_pins:
                    if not isinstance(pin, int):
                        raise TypeError("Each trigger_pin must be an integer")
                    if not (1 <= pin <= 28):
                        raise ValueError("Each trigger_pin must be an integer between 1 and 28 inclusive")

                # Further code that uses trigger_pins if they are valid
                print(f"trigger_pins are valid: {trigger_pins}")

                try:
                    import RPi.GPIO as GPIO
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
                        GPIO.add_event_detect(pin, gpio_event, callback=self.__set_stop_rotate, bouncetime=50)

                    self.__mode = mode
                except Exception as e:
                    try:
                        GPIO.cleanup()
                    except:
                        pass
                    print(f"An error occurred: {e}")
                    print(f"GPIO setting failed'")

            except Exception as e:
                try:
                    GPIO.cleanup()
                except:
                    pass
                print(f"An error occurred: {e}")
                print(f"trigger mode set to default: 'timed'")
        else:
            try:
                GPIO.cleanup()
            except:
                pass

    def __set_stop_rotate(self, channel):
        print(f"Trigger event detected on pin {channel}")
        self.__stop_rotate = True

    def set_index(self, index: int):
        if not (0 <= index <= 15):
            raise ValueError("Index must be within 0-15")
        self.index = index

    def dispense(self):
        if self.is_connected:
            if self.__mode == "timed":
                self.kit.servo[self.index].angle = 90
                time.sleep(3)
                self.kit.servo[self.index].angle = 0
                time.sleep(1)
                self.kit.servo[self.index].angle = 90
            elif self.__mode == "triggered":
                while True:
                    if self.__stop_rotate:
                        self.kit.servo[self.index].angle = 90
                        print("Stopped Rotation")
                        time.sleep(0.1)
                        break
                    else:
                        self.kit.servo[self.index].angle = 0
                        time.sleep(0.5)
        else:
            if self.__mode == "timed":
                print("Simulating...")
                print("Rotate 90")
                print("Sleep 3")
                time.sleep(3)
                print("Rotate 0")
                print("Sleep 1")
                time.sleep(1)
                print("Rotate 90")
            if self.__mode == "triggered":
                print("Simulating...")
                while True:
                    if self.__stop_rotate:
                        print("Rotate 90")
                        print("Stopped Rotation")
                        time.sleep(0.1)
                        break
                    else:
                        print("Rotate 90")
                        time.sleep(0.5)



class Coin_Slot_Control():
    def __init__(self, device_addr, baud, timeout = 0) -> None:
        self.device_addr = device_addr
        self.baud = baud
        self.timeout = timeout
        self.is_connected = False
        self._data = ""
        self.change = ""
        self.check_change = False

    @property
    def can_give_change(self, reset_input_buffer_at_start = False) -> bool:
        global data
        # print(f"Can give change of: {self.check_change}")
        return True

    def start_connection(self) -> bool:
        try:
            # self.ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1.0) # Hi Shane kapag di gumana yung sa baba try mo ito
            self.ser = serial.Serial(self.device_addr, self.baud, timeout = self.timeout)
            time.sleep(2)
            self.ser.reset_input_buffer()
            self.is_connected = True
            return self.is_connected
        except Exception as e:
            print (e)
            return self.is_connected


    def get_updates(self, reset_input_buffer_at_start = False):
        global data
        # print(f"Called function get_updates at: {self.__class__.__name__}")
        while self.is_connected:
            if reset_input_buffer_at_start:
                self.ser.reset_input_buffer()
            received_data = self.ser.readline().decode().strip()
            if received_data:
                self._data = received_data
                data = received_data

    def get_update(self, reset_input_buffer_at_start = False):
        global data
        received_data = ""
        # print(f"Called function get_updates at: {self.__class__.__name__}")
        if self.is_connected:
            if reset_input_buffer_at_start:
                self.ser.reset_input_buffer()
            received_data = self.ser.readline().decode()
            if received_data:
                self._data = received_data
                data = received_data
        return received_data
    
    @property
    def data(self):
        return self._data
    
    def send_update(self, data:str, reset_input_buffer_at_start = False) -> bool:
        if self.is_connected:
            try: 
                self.ser.write(data.encode())
                print(data)
                return True
            except Exception as e:
                print(f"Error on serial print with error: {e} and msg: {data}")
                return False
        else: 
            print(f"NO CONNECTION TO MODULE | Mock serial print: {data.encode()}")
            return True

    
class Gcash_Control(Coin_Slot_Control):

    def __init__(self, device_addr, baud, timeout=0.1) -> None:
        super().__init__(device_addr, baud, timeout)
    def dispense_change(self, amount) -> bool:
        print(f"Called function dispense_change at: {self.__class__.__name__}")
        print(f"No current procedure")
        print(f"Simulation: PROHIBITED REQUEST")
        return False


