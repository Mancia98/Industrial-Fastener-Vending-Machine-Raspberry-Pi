from hardware_interface import Servo_Control


servo_instance = Servo_Control()
servo_instance.start_connection()
servo_instance.set_mode("triggered", [16, 20, 19], "RISING")
servo_instance.set_index(3)
servo_instance.dispense()