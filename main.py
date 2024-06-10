import tkinter as tk
from PIL import Image, ImageTk
from helper_lib import *
from hardware_interface import *
import time
import threading
from datetime import datetime
import pytz
import json
from datetime import datetime


from hardware_interface import *


from lib.postgresql_adapter import Data_Base_Connection


__author__ = "Kenneth B. Mancia <manciakennethbarrun@outlook.com>"
__status__  = "development"
__version__ = "2.5.0"
__date__    = "02 May 2024"
__software_name__ = "FASTNER_VENDING_MACHINE"


#code setup
ENV = "DEV"

#global data containers 
item_descriptions:dict = {}

buttons:dict = {}
pay_mode_pages:dict = {}
payment_pages_screen:dict = {}
coin_payment_pages_screen:dict = {}
online_payment_pages:dict = {}
price_lbs:dict = {}
# running_transaction_state:str = "-1" # -1 set transaction state no "IDLE" or N/A | is default
payment_page_obj = object
# transcation_page_obj = object
# running_session_id:str = ""

coin_change_servo_stop = False

coin_module_run = False

sync_halt = False



str_money = "0"

thread_run_flag =  False


class Pay_Mode_Page:
    def __init__(self, key):
        self.key = key
        
    def show_pay_mode_page(self):
        global running_transaction_state
        running_transaction_state = self.__class__.__name__
        pay_mode_page_screen = tk.Toplevel()
        pay_mode_page_screen.attributes(window_configuration, True)
        payment_frame = tk.LabelFrame(pay_mode_page_screen, text="CHOOSE PAYMENT METHOD", font=('Arial', 20))
        payment_frame.pack(expand=True)        
        command = lambda: None
        text = "UNAVAILABLE"
        bg = 'seashell3'
        if coin_payment:
            self.coins_payment = Coins_Payment_Page(self.key)
            command = self.coins_payment.show_pay_page
            text = "COINS"
            bg = "white"
        coins_btn = tk.Button(payment_frame, text=text, bg=bg, width=30, height=5, command=command)
        command = lambda: None
        text = "UNAVAILABLE"
        bg = 'seashell3'
        if gcash_payment:
            self.online_payment = Gcash_Payment_Page(self.key, False)
            command = self.online_payment.show_pay_page
            text = "GCASH"
            bg = "white"
        gcash_btn = tk.Button(payment_frame, text=text, bg=bg, width=30, height=5, command=command)
        back_btn = tk.Button(pay_mode_page_screen, text="BACK", width=15, height=3, command=pay_mode_page_screen.destroy, bg="#FF4040")
        coins_btn.grid(row=0, column=0, sticky="WE")
        gcash_btn.grid(row=0, column=1, sticky="WE")
        back_btn.pack(side='left', padx=15, pady=15)
        #print(f"\nClicked Item ID = {self.key}")


class Payment_Page:
    def __init__(self, key, is_cash:bool = True):
        global items, grids
        items, grids = get_json_data(item_path, grid_path)
        print(f"Instantiated {self.__class__.__name__} Class with, ID: {key} Items: {items['items'][key]}")
        self.key = key
        self.price = items['items'][key]['item_price']
        self.flg_is_cash:bool= is_cash
        if is_cash:
            self.payment_type = "CASH"
        else:
            self.payment_type = "ONLINE"
        self.lbl_pay_method = f"PAYMENT METHOD ({self.payment_type})"
        self.lbl_pay_title = "PLEASE INSERT COINS..."
        pass
    def show_pay_page(self):
        global str_money, payment_page_obj, running_session_id, items, grids, sync_halt
        sync_halt = True
        items, grids = get_json_data(item_path, grid_path)
        print(f"Called function show_pay_page | Class with, ID: {self.key} Items: {items['items'][self.key]}")
        self.item_name = items['items'][self.key]['item_name']
        self.item_desc = items['items'][self.key]['item_size']
        self.item_price = items['items'][self.key]['item_price']
        try:
            self.transcation_page_obj = Transaction(self.key,
                                                    self.item_name,
                                                    self.item_desc,
                                                    self.item_price,
                                                    items['items'][self.key]['inventory'],
                                                    self.payment_type)
        except:
            print(f"Existing Payment page at: {self.__class__.__name__}")
            print("Order will not continue execution. \nPlease close existing payment session or restart application to reset.")
        else:
            running_session_id = self.key
            pay_page = tk.Toplevel()
            self.page = pay_page
            pay_page.protocol("WM_DELETE_WINDOW", self.close_page)
            pay_page.attributes(window_configuration, True)
            data_frame = tk.LabelFrame(pay_page, text=self.lbl_pay_method, font=('Arial', 20))
            data_frame.pack(expand=True)
            if not self.flg_is_cash:
                # img_obg = ImageTk.PhotoImage(Image.open(qr_path))
                resized_img = Image.open(qr_path).resize((qr_size[0], qr_size[1]))
                img_obg = ImageTk.PhotoImage(resized_img)
                label = tk.Label(data_frame, image=img_obg)
                label.image = img_obg
                label.pack()
            lb1 = tk.Label(data_frame, text=self.lbl_pay_title)
            # price_lb = Label(data_frame, text=self.lbl_price)
            self.lbl_price = f"Price: ₱{items['items'][self.key]['item_price']}"
            price_lbs[self.key] = tk.Label(data_frame, text=self.lbl_price)
            price_lb = price_lbs[self.key]
            self.money_lb = tk.Label(data_frame, text="Money received: " + str_money)
            back_btn = tk.Button(pay_page, text="BACK", width=15, height=3, command=self.close_page, bg="#FF4040")
            dispense_btn = tk.Button(pay_page, text="DISPENSE", width=15, height=3, command=self.transcation_page_obj.proceed, bg="#46FF40")
            lb1.pack()
            price_lb.pack()
            self.money_lb.pack()
            back_btn.pack(side='left', padx=15, pady=15)
            dispense_btn.pack(side='right', padx=15, pady=15)
            self.page = pay_page
            payment_page_obj = self
        
    def close_page(self):
        self.page.destroy()
        self.transcation_page_obj.close_page()
        Transaction.clear_instance()
        Transaction_Info.clear_instance()
        Singleton.clear_instance()
        print(f"Close page routine at: {self.__class__.__name__}")
    def refresh(self):
        global str_money
        # self.page.destroy()
        # self.show_pay_page()
        self.money_lb.config(text="Money received: " + str_money)

        
class Coins_Payment_Page(Payment_Page):
    def __init__(self, id, is_cash: bool = True):
        super().__init__(id, is_cash)
        self.lbl_pay_title = "PLEASE INSERT COINS..."
        self.lbl_pay_method = "PAYMENT METHOD (COINS)"


class Gcash_Payment_Page(Payment_Page):
    def __init__(self, id, is_cash: bool = True):
        super().__init__(id, is_cash)
        self.lbl_pay_title = "PLEASE SCAN THE QR CODE..."
        self.payment_type = "GCASH"
        self.lbl_pay_method = "PAYMENT METHOD (GCASH)"


class Transaction(Singleton):
    def __init__(self, key, item_name:str, item_desc:str, item_price:str, inventory_count:str, payment_type:str) -> None:
        super().__init__()
        global str_money
        self.key = key
        self.item_name = item_name
        self.item_desc = item_desc
        self.item_price = item_price
        self.item_amount = 1
        self.inventory_count = inventory_count
        self.payment_type = payment_type
        self.money = int(str_money)
        self.price = int(item_price)
        self.transaction_info = Transaction_Info(self.key,
                                            self.item_name,
                                            self.item_desc,
                                            self.item_price,
                                            self.item_amount,
                                            self.inventory_count,
                                            self.payment_type)
        self.transaction_id = self.transaction_info._get_transaction_id()
        print(f"{self.__class__.__name__} Initialized with Transaction Info ID: {self.transaction_id}")
        
        # Single run "proceed" atrribute lock flag.
        self.__proceed_lock = False
        
        # Single run "proceed" low change bank flag.
        self.low_change_warn = False    
    
    def proceed(self):
        global sync_halt
        sync_halt = True
        if self.payment_type == "COINS" or self.payment_type == "CASH":
            change_enable = coin_change
        else:
            change_enable = gcash_change
        print(change_enable)
        data, value = coins_management.get_all_coin_counts()
        if not self.low_change_warn and change_enable:
            if int(value) <= 20:
                print("WARNING BOX")
                warning_box("Low Level of Coins!\nPossibility of no change will be dispensed")
                self.low_change_warn = True
                return None
            

        global str_money
        self.money = int(str_money)
        # print(f"Event Proceed at: {self.__class__.__name__}")
        if not self.__proceed_lock:
            # coin_module.check_change = self.money >= self.price
            # if self.money >= self.price and coin_module.can_give_change:
            if self.money >= self.price:

                self.__proceed_lock = True
                change = self.money - self.price
                coins_management.change = change
                self.can_change = coins_management.can_dispense_change(None)
                try:
                    self.end_transaction = End_Transaction(self,self.key, change_enable)                
                    self.transaction_info.update_transaction_status(self.transaction_id, self.money, change, "SUCCESS")
                    items_handler.update_inventory(self.key, (int(self.inventory_count) - int(self.item_amount)))   
                    # update_json(self.key, "inventory", (int(self.inventory_count) - int(self.item_amount)), item_path)
                except:
                    print("Transaction Update Failed")
                    self.close_page()
                else:
                    transaction_routine(self)   
            else:
                if self.money <= self.price:
                    warning_box()
                else:
                    warning_box("Machine Cannot Dispense Enough Change")
                    self.close_page()
        else:
            warning_box("Cannot Start new Transaction\nPlease close all running transactions")
                
    def close_page(self):
        global sync_halt
        Transaction.clear_instance()
        Transaction_Info.clear_instance()
        Singleton.clear_instance()
        print(f"Close page routine at: {self.__class__.__name__}")
        sync_halt = False


class Transaction_Info(Singleton):

    def __init__(self,
                 item_key,
                 item_name,
                 item_description,
                 item_price,
                 item_amount,
                 inventory_count,
                 payment_type:str
                 ):
        self.__transaction_id = generate_datetime_string()
        self.__item_name = item_name
        self.__item_description = item_description
        self.__item_price = item_price
        self.__item_amount = item_amount
        self.__item_key = item_key
        self.__money = 0
        self.__change = 0
        self.__status = ""
        self.__inventory_count = inventory_count
        self.__payment_type = payment_type.upper()
        self.__hostname = get_hostname()
        self.__local_ip_address = get_local_ip()
        self.__internet_address = get_public_ip()

    def _get_transaction_id(self):
        return self.__transaction_id
    
    def get_transaction_info(self, key) -> list:
        if key == self.__transaction_id:
            payload = [self.__transaction_id,
                       self.__item_name,
                       self.__item_description,
                       self.__item_price,
                       self.__item_amount,
                       self.__item_key,
                       self.__money,
                       self.__change,
                       self.__payment_type,
                       self.__status,
                       self.__inventory_count,
                       self.__hostname,
                       self.__local_ip_address,
                       self.__internet_address]
            return payload
        else:
            return ["key failed!"]
        
    def update_transaction_status(self, key, money, change, status) -> bool:
        if key == self.__transaction_id:
            self.__money = money
            self.__change = change
            self.__status = str(status)
            return True
        else:
            return False
    
    def publish(self) -> bool:
        global record_path
        # if key == self.__transaction_id:
        if self.__transaction_id:
            #RECORD_ID,ITEM_NAME,ITEM_DESCRIPTION,ITEM_PRICE,ITEM_AMOUNT,ITEM_KEY,REGISTERED_MONEY,REGISTERED_CHANGE,TRANSACTION_STATUS,ITEM_INVENTORY
            payload = self.get_transaction_info(self.__transaction_id)
            appender = CSV_Interface(record_path)
            appender.items = payload
            if appender.insert():
                print("PASS TRANSACTION ID PASS IN APPEND")
                return True
            else:
                print("PASS TRANSACTION ID FAILED IN APPEND")
                return False
        else:
            print("Failed to publish data to CSV")
            return False
        
    def publish_database(self, payload:list = None) -> bool:

        if payload:
            payload = payload
        else:
            if self.__transaction_id:
                #RECORD_ID,ITEM_NAME,ITEM_DESCRIPTION,ITEM_PRICE,ITEM_AMOUNT,ITEM_KEY,REGISTERED_MONEY,REGISTERED_CHANGE,TRANSACTION_STATUS,ITEM_INVENTORY
                payload = self.get_transaction_info(self.__transaction_id)
            else:
                print("NO TRANSACTION ID OR PAYLOAD PASSED TO THIS FUNCTION")
                return False

        insert_statement = f"""
                            INSERT INTO TBL_TRANSACTION_RECORD VALUES (
                                TO_TIMESTAMP('{payload[0]}', 'YYYYMMDD-HH24MISS'), 
                                '{payload[1]}', 
                                '{payload[2]}', 
                                {payload[3]}, 
                                {payload[4]}, 
                                '{payload[5]}', 
                                {payload[6]}, 
                                {payload[7]}, 
                                '{payload[8]}', 
                                '{payload[9]}', 
                                {payload[10]}, 
                                '{payload[11]}', 
                                '{payload[12]}'::INET, 
                                '{payload[13]}'::INET
                            );
                            """
        print("here")                    
        if db_records_communication_obj.insert(insert_statement):
            print("PASS TRANSACTION ID DB UPLOAD")
            print(db_records_communication_obj.log)
            return True
        else:
            print("PASS TRANSACTION ID FAILED DB UPLOAD")
            print(db_records_communication_obj.log)
            return False

    def close_page(self):
        Transaction_Info.clear_instance()
        Singleton.clear_instance()
        print(f"Close page routine at: {self.__class__.__name__}")


class End_Transaction:
    def __init__(self,parent_obj:object, key:str, change_enable = True ) -> None:
        self.parent_obj:Transaction = parent_obj
        self.key = key
        self.change_enable = change_enable
        self.retain_balance_flg = False
    def dispense_change(self):
        global str_money
        self.change_page = tk.Toplevel()
        self.change_page.protocol("WM_DELETE_WINDOW", self.finish_transaction)
        self.change_page.attributes(window_configuration, True)
        change_frame = tk.LabelFrame(self.change_page, text="ITEM DISPENSED SUCCESSFULLY", font=('Arial', 20))
        change_frame.pack(expand=True)
        ############################### CHANGE ENABLED ROUTINE
        text = "Tap \"DONE\" button to dispense your change."
        left_command = self.dispense_finish
        right_command = self.retain_balance_cmd
        right_command_lbl = "RETAIN BALANCE"
        text_change = "Your change: " + str(coins_management.change)
        ############################### CHANGE DISABLED ROUTINE
        if not self.change_enable:
            text = "Tap \"DONE\" No change is availble for this payment type."
            left_command = self.finish_transaction
            right_command = lambda: None
            right_command_lbl = ""
            text_change = "Remaining balance is cleared"
        tap_lb = tk.Label(change_frame, text=text)
        change_lb = tk.Label(change_frame, text=text_change)
        done = tk.Button(self.change_page, text="DONE", width=15, height=3, bg="#46FF40", command=left_command)
        back = tk.Button(self.change_page, text=right_command_lbl, width=15, height=3, bg="#FF4040", command=right_command)
        tap_lb.pack()
        change_lb.pack()
        back.pack(side='left', padx=15, pady=15)
        done.pack(side='right', padx=15, pady=15)
    
    def retain_balance_cmd(self):
        self.retain_balance_flg = True
        print("RETAIN BALANCE EVENT BUTTON")
        self.finish_transaction()
    
    def dispense_finish(self):
        value = coins_management.can_dispense_change(None)
        if value:
            coins_management.execute_dispense_change(value)
            coins_management.execute_dispense_change_hardware()
        else:
            warning_box("Sorry, unable to dispense change")
            
            
        # coin_module.dispense_change()
        time.sleep(1)
        self.finish_transaction()

    
    def finish_transaction(self):
        global sync_halt
        if not self.retain_balance_flg:   
            clear_money()
        else:
            clear_money()
            add_money(coins_management.change)
        self.parent_obj.close_page()
        self.change_page.destroy()
        destroy_all()
        items, grids = get_json_data(item_path, grid_path)
        update_grid(items["items"], grids["buttons"])
        sync_halt = False
        # if isinstance(payment_page_obj, Payment_Page):
        #     try:
        #         window.update()
        #         payment_page_obj.refresh()
        #     except:
        #         print("Payment_Page_is not active")
        #     else:
        #         #command if there are no errors raised
        #         pass

    
class Coin_Handler:
    def __init__(self, coins_json_file):
        self.json_filename = coins_json_file
        self.local_json_data:dict = None
        self.__load_json_file()
        self.change = 0
        # If JSON file doesn't exist, create it based on database data
        if self.local_json_data is None:
            print("JSON file does not exist. Creating a new file based on database data...")
            self.__create_json_file_from_db()
        
    def __create_json_file_from_db(self):
        data_from_db = self.__fetch_data_from_db()
        if data_from_db:
            json_data_new = {"coins": {}}
            json_data_new["coins"] = {
                    "1": int(data_from_db[0][1]),
                    "5": int(data_from_db[0][2]),
                    "10": int(data_from_db[0][3]),
                    "20": int(data_from_db[0][4])
                }
            self.__save_json_file(json_data_new)
            print("JSON file created successfully based on database data.")
        else:
            print("Failed to fetch data from the database.")      
        
    def __load_json_file(self):
        try:
            with open(self.json_filename, "r") as json_file:
                self.local_json_data = json.load(json_file)
                # self.coins = {str(k): v for k, v in self.local_json_data.get("coins", {'1': 0, '5': 0, '10': 0, '20': 0}).items()}
                return self.local_json_data
            # return self.local_json_data.get("last_updated", "1970-01-01T00:00:00.000Z")
        except FileNotFoundError:
            # return "1970-01-01T00:00:00.000Z"
            self.local_json_data = None
            return self.local_json_data
        
    def __save_json_file(self, data):
        local_tz = pytz.timezone('Asia/Shanghai')  # Assuming GMT+8 is Asia/Shanghai timezone
        current_time = datetime.now(local_tz)  # Get current time in the specified timezone
        data["updates"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Update the timestamp
        with open(self.json_filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)

    def __fetch_data_from_db(self):
        if db_coin_communication_obj.connect():
            query_statement = (
                r"SELECT * FROM tbl_coin WHERE parent_key = '0';"
                )
            data_from_db = db_coin_communication_obj.query(query_statement)
            db_coin_communication_obj.disconnect()
            return data_from_db
        else:
            print("Failed to connect to the database.")
            return None
            
    def __update_db_from_json(self, updates: dict):
        if db_coin_communication_obj.connect():
            update_statement = f"""
            UPDATE tbl_coin
            SET coin_count_01 = {updates.get('1')},
                coin_count_05 = {updates.get('5')},
                coin_count_10 = {updates.get('10')},
                coin_count_20 = {updates.get('20')}
            WHERE parent_key = '0'
            """
            if db_coin_communication_obj.insert(update_statement):
                    print("Database updated successfully.")
            else:
                print("Failed to update the database.")
            db_coin_communication_obj.disconnect()
        else:
            print("Failed to connect to the database.")
    
    def sync(self):
        
    
        data_from_db = self.__fetch_data_from_db()
        local_json_data = self.__load_json_file()

        if data_from_db and local_json_data:
            json_data_new = {"coins": {}}
            json_data_new["coins"] = {
                    "1": int(data_from_db[0][1]),
                    "5": int(data_from_db[0][2]),
                    "10": int(data_from_db[0][3]),
                    "20": int(data_from_db[0][4])
                }

            db_last_updated = data_from_db[0][6]

            if json_data_new["coins"] != local_json_data["coins"]:
                if "updates" in local_json_data:
                    json_last_updated = datetime.strptime(local_json_data["updates"], "%Y-%m-%d %H:%M:%S")
                    if json_last_updated > db_last_updated:
                        updates = {"1": local_json_data["coins"]["1"],
                                   "5": local_json_data["coins"]["5"],
                                   "10": local_json_data["coins"]["10"],
                                   "20": local_json_data["coins"]["20"],
                                   }
                        self.__update_db_from_json(updates)
                        print("DB updated from JSON.") 
                    else:
                        self.__save_json_file(json_data_new)
                        print("JSON updated from Database.") 
                else:
                    print("No 'updates' timestamp found in the JSON file.")
                    self.__save_json_file(json_data_new)
            else:
                print("Data is the same, no need to sync.")
                return local_json_data, -1
        else:
            print("Failed to fetch data from the database or load JSON file.")
            # print(f"DB DATA: {data_from_db} | JSON DATA: {local_json_data}")
            return local_json_data, 0

        return local_json_data
   
    def get_coin_count(self, coin_type:str):
        if coin_type not in self.local_json_data["coins"]:
            raise ValueError(f"Invalid coin type: {coin_type}")
        return self.local_json_data["coins"][coin_type]

    def get_all_coin_counts(self):
        self.sync()
        c1 = [self.local_json_data["coins"]["1"]] * 1
        c5 = [self.local_json_data["coins"]["5"]] * 5
        c10= [self.local_json_data["coins"]["10"]] * 10
        c20 = [self.local_json_data["coins"]["20"]] * 20
        total_balance = sum(c1 + c5 + c10 + c20)
        return self.local_json_data["coins"],total_balance
    
    def can_dispense_change(self, amount: None):
        if not amount:
            amount = self.change
        self.sync()  # Ensure data is up-to-date
        change_dict = {}
        coins = sorted([int(k) for k in self.local_json_data["coins"].keys()], reverse=True)
        change_copy = self.local_json_data["coins"].copy()

        for coin in coins:
            if amount <= 0:
                break
            num_coins = min(change_copy[str(coin)], amount // coin)
            if num_coins > 0:
                change_dict[str(coin)] = num_coins
                amount -= num_coins * coin

        if amount == 0:
            return change_dict
        else:
            return False

    def execute_dispense_change(self, change_dict):
        if change_dict:
            self.change_dict = change_dict
            for coin, count in change_dict.items():
                self.local_json_data["coins"][coin] -= count
            self.__save_json_file(self.local_json_data)
            self.__update_db_from_json(self.local_json_data["coins"])
            return True
        else:
            return False
    
    def execute_dispense_change_hardware(self):
        coin_module_engine_stop()
        # for items in self.change_dict.items():
        #     print(items)
        #     data = (f"{str(items[0])}:{str(items[1])}")
        data_list = []
        for key, value in self.change_dict.items():
            data_list.append(f"{key}:{value}")
        data = ",".join(data_list)
        if coin_module.send_update(data):
            coin_change_servo_stop = False
            start_time = time.time()  # Record the start time
            target_time = start_time + 60  # One minute later
            while (not coin_change_servo_stop) and time.time() < target_time:
                pass
        else:
            pass
    
        
            


class Items_Handler:
    def __init__(self, items_json_file):
        self.json_filename = items_json_file
        self.__load_json_file()
        # If JSON file doesn't exist, create it based on database data
        if self.local_json_data is None:
            print("JSON file does not exist. Creating a new file based on database data...")
            self.__create_json_file_from_db()

    def __load_json_file(self):
        try:
            with open(self.json_filename, "r") as json_file:
                self.local_json_data = json.load(json_file)
                return self.local_json_data
        except FileNotFoundError:
            self.local_json_data = None
            return self.local_json_data

    def __create_json_file_from_db(self):
        data_from_db = self.__fetch_data_from_db()
        if data_from_db:
            json_data_new = {"items": {}}
            for row in data_from_db:
                item_key = row[0]
                json_data_new["items"][item_key] = {
                    "id": int(item_key),
                    "item_name": row[1],
                    "item_size": row[2],
                    "item_price": int(row[4]),
                    "inventory": row[3],
                    "available": row[5]
                }
            self.__save_json_file(json_data_new)
            print("JSON file created successfully based on database data.")
        else:
            print("Failed to fetch data from the database.")

    def __save_json_file(self, data):
        data["updates"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Update the timestamp
        with open(self.json_filename, "w") as json_file:
            json.dump(data, json_file, indent=4)

    def __fetch_data_from_db(self):
        if db_items_communication_obj.connect():
            query_statement = (
                r"SELECT tbl_inventory_writable_view.item_key, tbl_inventory_writable_view.item_name, "
                r"tbl_item_detail.item_desc, tbl_inventory_writable_view.total_item_amount, "
                r"tbl_inventory_writable_view.item_price, tbl_inventory_writable_view.enabled, "
                r"tbl_inventory_writable_view.last_updated "
                r"FROM tbl_inventory_writable_view "
                r"LEFT JOIN tbl_item_detail ON tbl_inventory_writable_view.item_name = tbl_item_detail.item_name "
                r"ORDER BY CASE WHEN ITEM_KEY ~ '^\d+$' THEN "
                r"CASE ITEM_KEY WHEN '0' THEN 0 WHEN '1' THEN 1 WHEN '2' THEN 2 WHEN '3' THEN 3 "
                r"WHEN '4' THEN 4 WHEN '5' THEN 5 WHEN '6' THEN 6 WHEN '7' THEN 7 WHEN '8' THEN 8 "
                r"WHEN '9' THEN 9 WHEN '10' THEN 10 WHEN '11' THEN 11 ELSE 9999 END "
                r"ELSE 10000 + ITEM_KEY::int END;"
            )
            data_from_db = db_items_communication_obj.query(query_statement)
            db_items_communication_obj.disconnect()
            return data_from_db
        else:
            print("Failed to connect to the database.")
            return None

    def __update_db_from_json(self, updates):
        if db_items_communication_obj.connect():
            update_statements = [
                f"UPDATE tbl_inventory_live SET total_item_amount = {item_data['inventory']} WHERE item_key = '{item_key}'"
                for item_key, item_data in updates.items()
            ]
            if db_items_communication_obj.insert(update_statements):
                print("Database updated successfully.")
            else:
                print("Failed to update the database.")
            db_items_communication_obj.disconnect()
        else:
            print("Failed to connect to the database.")

    def sync(self):
        data_from_db = self.__fetch_data_from_db()
        local_json_data = self.__load_json_file()
        # print("ITEM SYNC: FIRST IF BLOCK")
        if data_from_db and local_json_data:
            json_data_new = {"items": {}}
            # print("ITEM SYNC: FIRST IF BLOCK | FOR LOOP")
            for row in data_from_db:
                item_key = row[0]
                json_data_new["items"][item_key] = {
                    "id": int(item_key),
                    "item_name": row[1],
                    "item_size": row[2],
                    "item_price": int(row[4]),
                    "inventory": row[3],
                    "available": row[5]
                }
            # print("ITEM SYNC: FIRST IF BLOCK | OUT FOR LOOP")
            db_last_updated = max([row[6] for row in data_from_db])

            # print("ITEM SYNC: SECOND IF BLOCK")
            if json_data_new["items"] != local_json_data["items"]:
                # print(local_json_data)
                if "updates" in local_json_data:
                    # print("ITEM SYNC: SECOND IF BLOCK | FIRST NESTED IF")
                    json_last_updated = datetime.strptime(local_json_data["updates"], "%Y-%m-%d %H:%M:%S")
                    if json_last_updated > db_last_updated:
                        # print("ITEM SYNC: SECOND IF BLOCK | FIRST NESTED IF | FIRST NESTED IF")
                        updates = {item_key: item_data for item_key, item_data in local_json_data["items"].items()}
                        # print(updates)
                        self.__update_db_from_json(updates)
                    else:
                        self.__save_json_file(json_data_new)
                        # print("JSON updated from Database.") 
                else:
                    print("No 'updates' timestamp found in the JSON file.")
                    self.__save_json_file(json_data_new)
                # print("ITEM SYNC: END OF SECOND IF BLOCK")
            else:
                # print("Data is the same, no need to sync.")

                return local_json_data, -1
        else:
            print("Failed to fetch data from the database or load JSON file.")
            # print(f"DB DATA: {data_from_db} | JSON DATA: {local_json_data}")
            return local_json_data, 0

        return local_json_data, 0
    
    def update_inventory(self, item_key, new_inventory):
        # Update database
        if db_items_communication_obj.connect():
            update_statement = f"UPDATE tbl_inventory_live SET total_item_amount = {new_inventory} WHERE item_key = '{item_key}'"
            if db_items_communication_obj.insert([update_statement]):
                print(f"Inventory for item with key '{item_key}' updated successfully in the database.")
            else:
                print(f"Failed to update inventory for item with key '{item_key}' in the database.")
            db_items_communication_obj.disconnect()
        else:
            print("Failed to connect to the database.")

        # Update JSON file
        local_json_data = self.__load_json_file()
        if local_json_data:
            if item_key in local_json_data["items"]:
                local_json_data["items"][item_key]["inventory"] = new_inventory
                self.__save_json_file(local_json_data)
                print(f"Inventory for item with key '{item_key}' updated successfully in the JSON file.")
            else:
                print(f"Item with key '{item_key}' not found in the JSON data.")
        else:
            print("Failed to load JSON data.")


class Sales:
    pass


class Environment_Variables:
    def __init__(self, env) -> None:
        item_path = path_fix("env.json")
        data_parser_env_data = Data_Parser()
        data_parser_env_data.update_from_json(item_path)
        self.raw_json_data = data_parser_env_data.items
        self.window_configuration = data_parser_env_data.items[env]["display"]["window_configuration"]
        self.qr_size = data_parser_env_data.items[env]["display"]["QR_size"]
        self.record_path = data_parser_env_data.items[env]["data_file_path"]["record_csv"]
        self.coin_path = data_parser_env_data.items[env]["data_file_path"]["coins_json"]
        self.item_path = data_parser_env_data.items[env]["data_file_path"]["items_json"]
        self.grid_path = data_parser_env_data.items[env]["data_file_path"]["grids_json"]
        self.qr_path = data_parser_env_data.items[env]["data_file_path"]["qr_png"]
        self.log_path = data_parser_env_data.items[env]["data_file_path"]["app_log"]
        self.coin_addr = data_parser_env_data.items[env]["device_modules"]["coin_slot"]
        self.gcash_addr = data_parser_env_data.items[env]["device_modules"]["gcash_module"]
        self.coin_bypass_flg = data_parser_env_data.items[env]["bypasses"]["coin_slot"]
        self.gcash_bypass_flg = data_parser_env_data.items[env]["bypasses"]["gcash_module"]
        self.servo_bypass_flg = data_parser_env_data.items[env]["bypasses"]["servokit"]
        self.gcash_payment_en = data_parser_env_data.items[env]["payment_method"]["gcash"]
        self.coin_payment_en = data_parser_env_data.items[env]["payment_method"]["coin"]
        self.coin_change_en = data_parser_env_data.items[env]["change_enable"]["coin"]
        self.gcash_change_en = data_parser_env_data.items[env]["change_enable"]["gcash"]
        self.coin_balance_reset = data_parser_env_data.items[env]["balance_reset"]["coin"]
        self.gcash_balance_reset = data_parser_env_data.items[env]["balance_reset"]["gcash"]


# Live console routine
def background_proc():
    print("Background proc called")
    global sync_halt
    while True:
        time.sleep(4)
        print(f"proc status: {sync_halt}")
        if not sync_halt:
            # print("COIN SYNC")
            coins_management.sync()
            # print("ITEM SYNC")
            data, flag = items_handler.sync()
            temp = data
            if not flag == -1:
                    items, grids = get_json_data(item_path, grid_path)
                    update_grid(items["items"], grids["buttons"])
                         



def coin_module_engine_stop():  
    global coin_change_servo_stop, coin_module_run
    coin_module_run = False
    
def coin_module_engine_start():
    global coin_change_servo_stop, coin_module_run
    coin_module_run = True
    module_coin_thread.start()
    
def coin_module_engine():  
    global str_money, coin_change_servo_stop, coin_module_run
    x = ""
    while coin_module_run:
        x = coin_module.get_update()
        # x = input("Input Money: ")
        if x.startswith("COINS"):
            print(x)
            x = x.split(":")[1]
            refresh_money(x)
            str_money = x
        elif x.startswith("CHANGE"):
            print(x)
            x = x.split(":")[1]
            if x == "DONE":
                coin_change_servo_stop = True
        elif x.upper() == "STOP":
            break
        else:
            pass
        if coin_module_run == False:
            break
        time.sleep(0.01)



def gcash_module_engine():  
    global str_money, data
    x = ""
    while True:
        x = coin_module.get_update()
        # x = input("Input Money: ")
        if x.startswith("GCASH"):
            print(x)
            x = x.split(":")[1]
            refresh_money(x)
            str_money = x
        elif x.upper() == "STOP":
            break
        else:
            pass
        time.sleep(0.01)

def transaction_routine(self:Transaction):
    #first try to upload all lapsed (offline) data to database
    try:
        file = CSV_Interface(record_path)
        file.parse()
        if file.items and db_records_communication_obj.connect():
            logger.debug(db_records_communication_obj)
            
            for item in file.items:
                print(item)
                self.transaction_info.publish_database(item)
                # Transaction_Info.publish_database(None, item)
            db_records_communication_obj.disconnect()
            file.clear()
    except:
        pass
    finally:
        db_records_communication_obj.connect()
        try:
            #try to execute transaction via database, log transaction online
            if self.transaction_info.publish_database():
                print("here?")
                print("Transaction Succesfully Published Online")
                servo_kit.set_index(int(self.key))
                servo_kit.dispense()   
                self.end_transaction.dispense_change()
                # if not self.end_transaction.retain_balance_flg:
                #     print(f"DB transaction: {self.end_transaction.retain_balance_flg}")     
                #     clear_money()
                self.__proceed_lock = False
                db_records_communication_obj.disconnect()
            #if database transaction failed, log transaction offline
            else:
                self.transaction_info.publish()
                print("Unccesfull DB publish")
                print("Transaction Published Offline")
                servo_kit.set_index(int(self.key))
                servo_kit.dispense()
                self.end_transaction.dispense_change()
                # if not self.end_transaction.retain_balance_flg:
                #     print(f"LOCAL transaction: {self.end_transaction.retain_balance_flg}")         
                #     clear_money()
                self.__proceed_lock = False
        except Exception as error:
            print(error)
            db_records_communication_obj.disconnect()
        db_records_communication_obj.disconnect()
    db_records_communication_obj.disconnect()


def app_engine():
    while True:
        pass



def warning_box(text = "Not Enough Money."):
    warning_top = tk.Toplevel()
    warning_top.title("Warning")
    # warning_top.geometry('250x100+510+280')
    warning_top.attributes(window_configuration, True)
    
    data_frame = tk.LabelFrame(warning_top, font=('Arial', 20))
    data_frame.pack(expand=True)


    l1 = tk.Label(data_frame, image="::tk::icons::warning")
    l1.grid(row=0, column=0, rowspan=3, pady=(7, 0), padx=(10, 30), sticky="NSEW")
    l2 = tk.Label(data_frame,text=text)
    l2.grid(row=0, column=1, rowspan=2, columnspan=3, pady=(7, 10), sticky="NSEW")
    b1 = tk.Button(data_frame,text="Ok",command=warning_top.destroy,width = 10)
    b1.grid(row=3, column=2, padx=(2, 35))



    # lb1 = Label(data_frame, text=self.lbl_pay_title)
    # # price_lb = Label(data_frame, text=self.lbl_price)
    # self.lbl_price = f"Price: ₱{items['items'][self.key]['item_price']}"
    # price_lbs[self.key] = Label(data_frame, text=self.lbl_price)
    # price_lb = price_lbs[self.key]
    # self.money_lb = Label(data_frame, text="Money received: " + str_money)
    # back_btn = Button(pay_page, text="BACK", width=15, height=3, command=self.close_page, bg="#FF4040")
    # dispense_btn = Button(pay_page, text="DISPENSE", width=15, height=3, command=self.transcation_page_obj.proceed, bg="#46FF40")
    # lb1.pack()
    # price_lb.pack()
    # self.money_lb.pack()
    # back_btn.pack(side='left', padx=15, pady=15)
    # dispense_btn.pack(side='right', padx=15, pady=15)


def draw_grid(items:dict,grids:dict, parent_process):
    for key, item in items.items():

        # Generates Instance Object of Payment Page per item
        pay_mode_pages[key] = Pay_Mode_Page(key)
        pay_mode_page:Pay_Mode_Page = pay_mode_pages[key]

        # Read Per Button Config
        w = grids[key]['width']
        h = grids[key]['height']
        r = grids[key]['row']
        c = grids[key]['column']
        stky = grids[key]['sticky']
        en:bool = item['available']
        bg = 'white'

         # Item Description Formatter
        if int(item['inventory']) < 1 and en:
            item_desc = f"{item['item_name']}\n{item['item_size']}\nNO STOCKS, UNAVAILABLE"
            bg = 'seashell3'
            command = (lambda: None)

        elif not en:
            item_desc = f"DISABLED"
            bg = 'seashell3'
            command = (lambda: None)
        else:
            item_desc = f"{item['item_name']}\n{item['item_size']}\n₱{item['item_price']}"
            bg = 'white'
            command = pay_mode_page.show_pay_mode_page

        # Keeps list of descriptions generated
        item_descriptions[key] = item_desc


        # Button Creator
        buttons[key] = tk.Button(parent_process, text=item_desc, width=w, height=h, bg=bg, command=command)
        button:tk.Button = buttons[key]
        button.grid(row=r, column=c, sticky=stky)


def update_grid(items:dict,grids:dict):
    for key, item in items.items():

        # Access objects per key before update
        button:tk.Button = buttons[key]

        # Access Instance Object of Payment Page per item
        pay_mode_page:Pay_Mode_Page = pay_mode_pages[key]

        # Read Per Button Config
        w = grids[key]['width']
        h = grids[key]['height']
        r = grids[key]['row']
        c = grids[key]['column']
        stky = grids[key]['sticky']
        en:bool = item['available']
        bg = 'white'

         # Item Description Formatter
        if int(item['inventory']) < 1 and en:
            item_desc = f"{item['item_name']}\n{item['item_size']}\nNO STOCKS, UNAVAILABLE"
            bg = 'seashell3'
            command = (lambda: None)

        elif not en:
            item_desc = f"DISABLED"
            bg = 'seashell3'
            command = (lambda: None)
        else:
            item_desc = f"{item['item_name']}\n{item['item_size']}\n₱{item['item_price']}"
            bg = 'white'
            command = pay_mode_page.show_pay_mode_page
        
        # Keeps list of descriptions generated
        item_descriptions[key] = item_desc

        # Access objects per key before update
        button:tk.Button = buttons[key]

        # Button update
        button.config(text=item_desc, width=w, height=h, bg=bg, command=command)

    #print("Update Draw")


def destroy_all():
    for widget in window.winfo_children():
        if isinstance(widget, tk.Toplevel):
            widget.destroy()


def refresh_money(money):
    global str_money, payment_page_obj
    str_money = money
    if isinstance(payment_page_obj, Payment_Page):
        try:
            window.update()
            payment_page_obj.refresh()
        except:
            print("Payment_Page_is not active")
        else:
            #command if there are no errors raised
            pass
    else:
        print("No instance of payment page")


def add_money(money_to_add):
    global str_money, payment_page_obj
    str_money = str(int(str_money) + int(money_to_add))
    if isinstance(payment_page_obj, Payment_Page):
        try:
            window.update()
            payment_page_obj.refresh()
        except:
            print("Payment_Page_is not active")
        else:
            #command if there are no errors raised
            pass
    else:
        print("No instance of payment page")


def clear_money():
    print("clear money called")

    global str_money, payment_page_obj
    str_money ="0"
    if isinstance(payment_page_obj, Payment_Page):
        try:
            window.update()
            payment_page_obj.refresh()
        except:
            print("Payment_Page_is not active")
        else:
            #command if there are no errors raised
            pass
    else:
        print("No instance of payment page")

    


# SCRIPT START

env_setup = Environment_Variables(ENV)
window_configuration = env_setup.window_configuration
qr_size:list = env_setup.qr_size
record_path = env_setup.record_path
coin_path = env_setup.coin_path
item_path = env_setup.item_path
grid_path = env_setup.grid_path
qr_path = env_setup.qr_path
log_path = env_setup.log_path
coin_dev_addr = env_setup.coin_addr
gcash_dev_addr = env_setup.gcash_addr
servo_bypass:bool = env_setup.servo_bypass_flg
coin_bypass:bool = env_setup.coin_bypass_flg
gcach_bypass:bool = env_setup.gcash_bypass_flg
gcash_payment = env_setup.gcash_payment_en
coin_payment = env_setup.coin_payment_en
gcash_change:bool = env_setup.gcash_change_en
coin_change:bool = env_setup.coin_change_en
coin_balance_reset = env_setup.coin_balance_reset
gcash_balance_reset = env_setup.gcash_balance_reset



print(path_fix(record_path))
print(path_fix(qr_path))



window_configuration = env_setup.window_configuration #-alpha, -transparentcolor, -disabled, -fullscreen, -toolwindow, or -topmost -zoomed 


# INITIALIZE SERIAL COMMUNICATION WITH ARDUINO
coin_module = Coin_Slot_Control(coin_dev_addr,9600)
gcash_module = Gcash_Control(gcash_dev_addr,9600)


# INITIALIZE COMMUNICATION WITH SERVO MOTOR CONTORLLER
servo_kit = Servo_Control()


# INITIALIZE LOGGING SERVICE
logger = Logging(__software_name__, log_path)
logger.debug("Sofware Startup")

# INITIALIZE DATABASE ADAPTER
# cn = Data_Base_Connection("client","!@_420693.1416_CLIent", "vending-machine", "35.221.157.72", sslmode="require", sslcert="database/client-cert.pem", sslkey="database/client-key.pem")
db_coin_communication_obj = Data_Base_Connection("client","!@_420693.1416_CLIent", "vending-machine", "35.221.157.72")
db_items_communication_obj = Data_Base_Connection("client","!@_420693.1416_CLIent", "vending-machine", "35.221.157.72")
db_records_communication_obj = Data_Base_Connection("client","!@_420693.1416_CLIent", "vending-machine", "35.221.157.72")



logger.debug(db_coin_communication_obj.log)
logger.debug(db_items_communication_obj.log)
logger.debug(db_records_communication_obj)

# INITIALIZE ITEM HANDLER DAEMON / SERVICE
items_handler = Items_Handler(item_path)

# INITIALIZE COIN HANDLER DAEMON / SERVICE\
coins_management = Coin_Handler(coin_path)


termninal_thread00 = threading.Thread(target=background_proc, daemon= True)
termninal_thread00.start()

window = tk.Tk()
window.title("INDUSTRIAL FASTENERS VENDING MACHINE")
window.attributes(window_configuration, True)


selection_frame = tk.LabelFrame(window,text="CHOOSE THE ITEM YOU WANT TO BUY", font=('Arial', 20))
selection_frame.pack(expand=True)
selection_frame.columnconfigure(0, weight=0)
selection_frame.rowconfigure(0, weight=1)


# This function is called to read data from json files that is used as item database for our application
logger.debug("Fetching info from, item and grid json files.")
items, grids = get_json_data(item_path, grid_path)

#This function is called to generate and draw buttons in the frame screen.
logger.debug("Generating Buttons.")
draw_grid(items["items"], grids["buttons"], selection_frame)
    
# START SERIAL COMMUNICATION WITH ARDUINO
if not coin_module.start_connection():
    if coin_bypass:
        str_money = "50"
        logger.warn("Communication with Coin Module Failed System will STILL continue without this feature!")
        warning_box("Communication with Coin Module Failed\nSystem will STILL continue without this feature!")
    else:
        logger.error("Communication with Coin Module Failed System will STILL continue without this feature!")
        print("Communication with Coin Module Failed\nSystem will NOT continue without this feature!\n")
        exit()

if not gcash_module.start_connection():
    if gcach_bypass:
        logger.warn("Communication with Gcash Module Failed System will STILL continue without this feature!")
        warning_box("Communication with Gcash Module Failed\nSystem will STILL continue without this feature!")
    else:
        logger.error("Communication with Gcash Module Failed\nSystem will NOT continue without this feature!")
        print("Communication with Gcash Module Failed\nSystem will NOT continue without this feature!\n")
        exit()

# START COMMUNICATION WITH SERVOKIT
if not servo_kit.start_connection():
    servo_kit.set_mode("triggered", [19], "RISING")
    if servo_bypass:
        logger.warn("Communication with ServoKit Failed System will STILL continue without this feature!")
        warning_box("Communication with ServoKit Failed\nSystem will STILL continue without this feature!")
    else:
        logger.error("Communication with ServoKit Failed System will NOT continue without this feature!")
        print("Communication with ServoKit Failed\nSystem will NOT continue without this feature!\n")
        exit()




logger.debug("Started thread: live money getter.")
module_coin_thread = threading.Thread(target=coin_module_engine, daemon=True)
# termninal_thread01.start()
module_gcash_thread = threading.Thread(target=gcash_module_engine, daemon=True)
# termninal_thread02.start()



window.mainloop()