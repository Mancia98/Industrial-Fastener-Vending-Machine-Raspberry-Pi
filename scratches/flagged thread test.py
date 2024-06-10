import time
import threading

flg1 = True

def thread1():
    count = 1
    while flg1:
        print(f"Flag1 is Running | Count: {count}")
        count += 1
        time.sleep(1)
thread1_thread = threading.Thread(target= thread1)

thread1_thread.start()

start_time = time.time()
target_time = start_time + 60

while True:
    if time.time() >= target_time:
        flg1 = False
        print("SATISFIED")
    
    "time checker"

    