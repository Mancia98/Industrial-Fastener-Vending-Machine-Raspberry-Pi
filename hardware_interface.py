import serial
import time
data = ""


# class Servo_Control():
#     def __init__(self) -> None:
#         self.is_connected = False
#         self.index = 0
#         self.set_index(16)
        
#     def start_connection(self) -> bool:
#         try:
#             from adafruit_servokit import ServoKit
#             self.kit = ServoKit(channels=16)
#             self.is_connected = True
#             print("ServoKit OK")
#         except:
#             from dummy_servokit import ServoKit
#             print("ServoKit Failed")
#         return self.is_connected
    
#     def set_index(self, index:int):
#         self.index = index
            
#     def dispense(self):
#         if self.is_connected:
#             self.kit.servo[self.index].angle = 90
#             time.sleep(3)
#             self.kit.servo[self.index].angle = 0
#             time.sleep(1)
#             self.kit.servo[self.index].angle = 90
#         else:
#             print("Simulting...")
#             print("Rotate 90")
#             print("Sleep 3")
#             time.sleep(3)
#             print("Rotate  0")
#             print("Sleep 1")
#             time.sleep(1)
#             print("Rotate 90")
        
#     def dispense2(self, index):
#         pass

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
    
    def set_mode(self, mode:str = "timed", trigger_pin:int = None, trigger_event:str = "RISING"):
        if mode == "triggered":
            try:
                if trigger_pin is None:
                    raise ValueError("The trigger_pin cannot be None")

                if not isinstance(trigger_pin, int):
                    raise TypeError("The trigger_pin must be an integer")

                if not (1 <= trigger_pin <= 28):
                    raise ValueError("The trigger_pin must be an integer between 1 and 28 inclusive")

                # Further code that uses trigger_pin if it is valid
                print(f"trigger_pin is valid: {trigger_pin}")

                try:
                    import RPi.GPIO as GPIO
                    GPIO.setmode(GPIO.BCM)
                    INPUT_PIN = trigger_pin
                    GPIO.setup(INPUT_PIN, GPIO.IN)
                    event_mapping = {
                        "RISING": GPIO.RISING,
                        "FALLING": GPIO.FALLING,
                        "BOTH": GPIO.BOTH
                    }

                    if trigger_event not in event_mapping:
                        raise ValueError(f"Invalid trigger_event: {trigger_event}")

                    gpio_event = event_mapping[trigger_event]
                    GPIO.add_event_detect(INPUT_PIN, gpio_event, callback=self.__set_stop_rotate, bouncetime=50)
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
                
            
    def __set_stop_rotate(self):
        self.__stop_rotate = True
    
    def set_index(self, index:int):
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
            if self.__mode == "triggered":
                while True:
                    if self.__stop_rotate:
                        self.kit.servo[self.index].angle = 90
                        print("Stopped Rotation")
                        time.sleep(0.1)
                        break
                    else:
                        self.kit.servo[self.index].angle = 0
        else:
            if self.__mode == "timed":
                print("Simulting...")
                print("Rotate 90")
                print("Sleep 3")
                time.sleep(3)
                print("Rotate  0")
                print("Sleep 1")
                time.sleep(1)
                print("Rotate 90")
            if self.__mode == "triggered":
                print("Simulting...")
                while True:
                    if self.__stop_rotate:
                        print("Rotate 90")
                        print("Stopped Rotation")
                        self.__stop_rotate = False
                        time.sleep(0.1)
                        break
                    else:
                        self.kit.servo[self.index].angle = 0

        
    def dispense2(self, index):
        pass


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
    
    def dispense_change(self) -> bool:
        amount = self.change
        print(f"Called function dispense_change at: {self.__class__.__name__}")
        print(f"No current procedure")
        print("j")
        print(f"Simulation: Dispensing {amount}")
        return True

    
class Gcash_Control(Coin_Slot_Control):

    def __init__(self, device_addr, baud, timeout=0.1) -> None:
        super().__init__(device_addr, baud, timeout)
    def dispense_change(self, amount) -> bool:
        print(f"Called function dispense_change at: {self.__class__.__name__}")
        print(f"No current procedure")
        print(f"Simulation: PROHIBITED REQUEST")
        return False


