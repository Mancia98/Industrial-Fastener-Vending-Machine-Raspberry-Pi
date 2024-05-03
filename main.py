import tkinter as tk
from PIL import Image, ImageTk
from helper_lib import *
from hardware_interface import *
from wallet import *
import time
import threading

__author__ = "Kenneth B. Mancia <manciakennethbarrun@outlook.com>"
__status__  = "development"
__version__ = "2.4.0"
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




str_money = "50"

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
        global str_money, payment_page_obj, running_session_id, items, grids
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
            pay_page.attributes(window_configuration, True)
            data_frame = tk.LabelFrame(pay_page, text=self.lbl_pay_method, font=('Arial', 20))
            data_frame.pack(expand=True)
            if not self.flg_is_cash:
                img_obg = ImageTk.PhotoImage(Image.open(qr_path))
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
    
    def proceed(self):
        global str_money
        self.money = int(str_money)
        # print(f"Event Proceed at: {self.__class__.__name__}")
        if not self.__proceed_lock:
            coin_module.check_change = self.money >= self.price
            if self.money >= self.price and coin_module.can_give_change:

                self.__proceed_lock = True
                change = self.money - self.price
                coin_module.change = change
                try:
                    if self.payment_type == "COINS" or self.payment_type == "CASH":
                        change_enable = coin_change
                    else:
                        change_enable = gcash_change
                    end_transaction = End_Transaction(self,self.key, change_enable)                
                    self.transaction_info.update_transaction_status(self.transaction_id, self.money, change, "SUCCESS")   
                    update_json(self.key, "inventory", (int(self.inventory_count) - int(self.item_amount)), item_path)
                except:
                    print("Transaction Update Failed")
                    self.close_page()
                else:
                    if self.transaction_info.publish():
                        servo_kit.set_index(self.key)
                        servo_kit.dispense()
                        str_money = "0"
                        end_transaction.dispense_change()
                        self.__proceed_lock = False
                    else:
                        print("unsucessful publish")   
            else:
                if coin_module.can_give_change:
                    warning_box()
                else:
                    warning_box("Machine Cannot Dispense Enough Change")
                    self.close_page()
        else:
            warning_box("Cannot Start new Transaction\nPlease close all running transactions")
                
    def close_page(self):
        Transaction.clear_instance()
        Transaction_Info.clear_instance()
        Singleton.clear_instance()
        print(f"Close page routine at: {self.__class__.__name__}")


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
        self.__item_price = str(item_price)
        self.__item_amount = str(item_amount)
        self.__item_key = str(item_key)
        self.__money = ""
        self.__change = ""
        self.__status = ""
        self.__inventory_count = str(inventory_count)
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
            self.__money = str(money)
            self.__change = str(change)
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
            appender = Data_Writer(record_path)
            appender.items = payload
            if appender.append_to_csv():
                print("PASS TRANSACTION ID PASS IN APPEND")
                return True
            else:
                print("PASS TRANSACTION ID FAILED IN APPEND")
                return False
        else:
            print("Failed to publish data to CSV")
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
    def dispense_change(self):
        global str_money
        self.change_page = tk.Toplevel()
        self.change_page.attributes(window_configuration, True)
        change_frame = tk.LabelFrame(self.change_page, text="ITEM DISPENSED SUCCESSFULLY", font=('Arial', 20))
        change_frame.pack(expand=True)
        text = "Tap \"DONE\" button to dispense your change."
        command = self.dispense_finish
        text_change = "Your change: " + str(coin_module.change)
        if not self.change_enable:
            text = "Tap \"DONE\" No change is availble for this payment type."
            command = self.finish_transaction
            text_change = "No Change"
        tap_lb = tk.Label(change_frame, text=text)
        change_lb = tk.Label(change_frame, text=text_change)
        back = tk.Button(self.change_page, text="BACK", width=15, height=3, bg="#FF4040", command=self.finish_transaction)
        done = tk.Button(self.change_page, text="DONE", width=15, height=3, bg="#46FF40", command=command)
        tap_lb.pack()
        change_lb.pack()
        back.pack(side='left', padx=15, pady=15)
        done.pack(side='right', padx=15, pady=15)
    
    def dispense_finish(self):
        coin_module.dispense_change()
        time.sleep(3)
        self.finish_transaction()

    
    def finish_transaction(self):
        self.parent_obj.close_page()
        self.change_page.destroy()
        destroy_all()
        items, grids = get_json_data(item_path, grid_path)
        update_grid(items["items"], grids["buttons"])
        if isinstance(payment_page_obj, Payment_Page):
            try:
                window.update()
                payment_page_obj.refresh()
            except:
                print("Payment_Page_is not active")
            else:
                #command if there are no errors raised
                pass
        

class Environment_Variables:
    def __init__(self, env) -> None:
        item_path = path_fix("env.json")
        data_parser_env_data = Data_Parser()
        data_parser_env_data.update_from_json(item_path)
        self.raw_json_data = data_parser_env_data.items
        self.window_configuration = data_parser_env_data.items[env]["display"]["window_configuration"]
        self.record_path = data_parser_env_data.items[env]["data_file_path"]["record_csv"]
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


# Live console routine
def get_item_desc():  
    global str_money
    # while True:
    #     x = input("name of the item: ")
    #     if x == "x":
    #         items, grids = get_json_data(item_path, grid_path)
    #         update_grid(items["items"], grids["buttons"])
    #         window.update()
    #     else:
    #         refresh_money(x)
    while True:
        x = input("Input Money: ")
        if x.isnumeric():
            # items, grids = get_json_data(item_path, grid_path)
            # update_grid(items["items"], grids["buttons"])
            # window.update()
            refresh_money(x)
        elif x.upper() == "STOP":
            break
        else:
            pass


def app_engine():
    while True:
        pass


def warning_box1(text = "Not Enough Money."):
    warning_top = tk.Toplevel()
    warning_top.title("Warning!")
    # warning_top.geometry('250x100+510+280')
    warning_top.attributes(window_configuration, True)

    l1 = tk.Label(warning_top, image="::tk::icons::warning")
    l1.grid(row=0, column=0, pady=(7, 0), padx=(10, 30), sticky="e")
    l2 = tk.Label(warning_top,text=text)
    l2.grid(row=0, column=1, columnspan=3, pady=(7, 10), sticky="w")
    b1 = tk.Button(warning_top,text="Ok",command=warning_top.destroy,width = 10)
    b1.grid(row=1, column=1, padx=(2, 35), sticky="w")


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
        en:bool = grids[key]['enabled']
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
        en:bool = grids[key]['enabled']
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

        
    


# SCRIPT START

env_setup = Environment_Variables(ENV)
window_configuration = env_setup.window_configuration
record_path = env_setup.record_path
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
gcash_change = env_setup.gcash_change_en
coin_change = env_setup.coin_change_en

print(path_fix(record_path))
print(path_fix(qr_path))



window_configuration = env_setup.window_configuration #-alpha, -transparentcolor, -disabled, -fullscreen, -toolwindow, or -topmost -zoomed 

# INITIALIZE SERIAL COMMUNICATION WITH ARDUINO

coin_module = Coin_Slot_Control(coin_dev_addr,9600, 1.0)
gcash_module = Gcash_Control(gcash_dev_addr,9600, 1.0)

# INITIALIZE COMMUNICATION WITH SERVO MOTOR CONTORLLER

servo_kit = Servo_Control()

logger = Logging(__software_name__, log_path)
logger.debug("Sofware Startup")


window = tk.Tk()
window.title("INDUSTRIAL FASTENERS VENDING MACHINE")
window.attributes(window_configuration, True)


selection_frame = tk.LabelFrame(window,text="CHOOSE THE ITEM YOU WANT TO BUY", font=('Arial', 20))
selection_frame.pack(expand=True)
selection_frame.columnconfigure(0, weight=0)
selection_frame.rowconfigure(0, weight=1)

logger.debug("Started thread: live money getter.")
termninal_thread = threading.Thread(target=get_item_desc, daemon=True)
termninal_thread.start()

# This function is called to read data from json files that is used as item database for our application
logger.debug("Fetching info from, item and grid json files.")
items, grids = get_json_data(item_path, grid_path)

#This function is called to generate and draw buttons in the frame screen.
logger.debug("Generating Buttons.")
draw_grid(items["items"], grids["buttons"], selection_frame)
    
# START SERIAL COMMUNICATION WITH ARDUINO
if not coin_module.start_connection():
    if coin_bypass:
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
    if servo_bypass:
        logger.warn("Communication with ServoKit Failed System will STILL continue without this feature!")
        warning_box("Communication with ServoKit Failed\nSystem will STILL continue without this feature!")
    else:
        logger.error("Communication with ServoKit Failed System will NOT continue without this feature!")
        print("Communication with ServoKit Failed\nSystem will NOT continue without this feature!\n")
        exit()



window.mainloop()