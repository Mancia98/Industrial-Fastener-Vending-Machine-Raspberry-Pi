import serial
import time


class Servo_Control():
    def __init__(self) -> None:
        self.is_connected = False
        self.index = 0
        self.set_index(16)
        
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
    
    def set_index(self, index:int):
        self.index = index
            
    def dispense(self):
        if self.is_connected:
            self.kit.servo[self.index].angle = 90
            time.sleep(3)
            self.kit.servo[self.index].angle = 0
            time.sleep(1)
            self.kit.servo[self.index].angle = 90
        else:
            print("Simulting...")
            print("Rotate 90")
            print("Sleep 3")
            time.sleep(3)
            print("Rotate  0")
            print("Sleep 1")
            time.sleep(1)
            print("Rotate 90")
        
    def dispense2(self, index):
        pass


class Coin_Slot_Control():
    def __init__(self, device_addr, baud, timeout = 1.0) -> None:
        self.device_addr = device_addr
        self.baud = baud
        self.timeout = timeout
        self.is_connected = False
        self._data = ""
        self.change = ""
        self.check_change = ""

    @property
    def can_give_change(self, reset_input_buffer_at_start = False) -> bool:
        global data
        print(f"Can give change of: {self.check_change}")
        return True

    def start_connection(self) -> bool:
        try:
            # self.ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1.0) # Hi Shane kapag di gumana yung sa baba try mo ito
            self.ser = serial.Serial(self.device_addr, self.baud, self.timeout)
            time.sleep(2)
            self.ser.reset_input_buffer()
            self.is_connected = True
            return self.is_connected
        except:
            return self.is_connected


    def get_updates(self, reset_input_buffer_at_start = False):
        global data
        print(f"Called function get_updates at: {self.__class__.__name__}")
        while self.is_connected:
            if reset_input_buffer_at_start:
                self.ser.reset_input_buffer()
            received_data = self.ser.readline().decode().strip()
            if received_data:
                self._data = received_data
                data = received_data
            time.sleep(0.1)
    
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


