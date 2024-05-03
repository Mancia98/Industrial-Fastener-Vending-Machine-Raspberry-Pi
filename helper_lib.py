import os
import json
import csv
from datetime import datetime
import socket
import platform
import logging
import aiohttp
import asyncio
import json

__software_name__ = "helper_library"

class Logging:

    def __init__(self, software_name, file_name):
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - [%(levelname)s] %(message)s')
        self.logger = logging.getLogger(software_name)
        self.logger.setLevel(logging.DEBUG)
        # Create a file handler and set its formatter
        file_handler = logging.FileHandler(path_fix(file_name))
        print(f"Created log file @: {path_fix(file_name)}")
        file_handler.setFormatter(self.formatter)
        # Add the file handler to the logger
        self.logger.addHandler(file_handler)

    def debug(self, msg):
        self.logger.debug(msg)
    
    def warn(self, msg):
        self.logger.warning(msg)
    
    def error(self, msg):
        self.logger.error(msg)       
    
    def critical(self, msg):
        self.logger.critical(msg)        


class Data_Parser:
    def __init__(self):
        self.items = {}

    def update_from_json(self, file_path):
        try:
            with open(file_path) as file:
                data = json.load(file)
                self.items = data
            print("Data updated successfully from JSON file.")
            # print(self.items)
        except FileNotFoundError:
            print(f"File '{file_path}' not found.")
        except Exception as e:
            print(f"An error occurred while updating data from JSON file: {e}")


class Data_Writer:
    def __init__(self,file_path) -> None:
        self.file_path = file_path
        self.items = []
        print(self.items)
        self.is_succes =False

    def create_csv(self) -> bool:
        try:
            with open(self.file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(self.items)
            self.is_succes = True   
            return self.is_succes
        except:
            print("CSV Creation Failed")
            return self.is_succes
        
    
    def append_to_csv(self) -> bool:
        # with open(self.file_path, mode='a', newline='') as file:
        #     writer = csv.writer(file)
        #     print(self.items)
        #     writer.writerows(self.items)
        try:
            with open(self.file_path, mode='a', newline='') as file:
                writer = csv.writer(file)
                print(self.items)
                writer.writerow(self.items)
            self.is_succes = True
            print(self.items)
            return self.is_succes
        except:
            print("CSV Update Failed")
            return self.is_succes


class App_Config_Parser:
    def __init__(self):
        pass


class Environment_Config_Parser:
    def __init__(self):
        pass


class Singleton:
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            return cls._instance
        else:
            raise RuntimeError("Singleton class already instantiated")

    @classmethod
    def clear_instance(cls):
        cls._instance = None


def path_fix(path:str):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, path)
    return file_path


def get_json_data(item_path, grid_path):
    data_parser_item_data = Data_Parser()
    data_parser_grid_data = Data_Parser()
    data_parser_item_data.update_from_json(path_fix(item_path))
    data_parser_grid_data.update_from_json(path_fix(grid_path))
    return data_parser_item_data.items, data_parser_grid_data.items


def update_json(item_id, key, value, file_path):
    """
    Update a specific key for an item in a JSON file.

    :param item_id: The ID of the item as an integer whose key needs to be updated.
    :param key: The key in the item dictionary to update.
    :param value: The new value to set for the specified key.
    :param file_path: Path to the JSON file (default is 'inventory_data.json').
    """
    try:
        # Convert item_id to string since JSON keys are stored as strings
        item_id = str(item_id)

        # Open the JSON file and load data
        with open(file_path, 'r') as file:
            data = json.load(file)

        # Check if the item exists in the JSON data
        if item_id in data['items']:
            # Check if the key exists for the item
            if key in data['items'][item_id]:
                # Update the key with the new value
                data['items'][item_id][key] = value
                # Write the updated data back to the file
                with open(file_path, 'w') as file:
                    json.dump(data, file, indent=4)
                print(f"{key} updated for item ID {item_id}.")
            else:
                print(f"Key '{key}' does not exist for item ID {item_id}.")
        else:
            print(f"No item found with ID {item_id}.")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the file {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")


def parse_string_to_list(input_string):
    # Remove leading and trailing whitespace
    input_string:str = input_string.strip()
    
    # Check if the string starts with '[' and ends with ']'
    if input_string.startswith('[') and input_string.endswith(']'):
        # Remove the '[' and ']' characters
        input_string = input_string[1:-1]
        
        # Split the string by ',' to get individual elements
        elements = input_string.split(',')
        
        # Remove leading and trailing whitespace from each element and add to the list
        parsed_list = [element.strip() for element in elements]
        
        return parsed_list
    else:
        # If the input string doesn't resemble a list, return None
        return None


def generate_datetime_string():
    now = datetime.now()
    date_string = now.strftime("%Y%m%d")
    time_string = now.strftime("%H%M%S")
    return f"{date_string}-{time_string}"


def get_hostname_socket():
    return socket.gethostname()


def get_hostname_os():
    # Use the system's environment variables or system command to get the hostname
    hostname = os.getenv('HOSTNAME')  # Try to get hostname from an environment variable
    if hostname is None:
        # Fallback if the HOSTNAME environment variable is not set
        hostname = os.popen('hostname').read().strip()
    return hostname


def get_local_ip_socket():
    try:
        # Create a socket to connect to an external site
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Use Google's public DNS server to find out our IP
            s.connect(("8.8.8.8", 80))
            # Get the socket's own address
            local_ip = s.getsockname()[0]
    except Exception as e:
        # local_ip = "Unable to determine local IP: " + str(e)
        local_ip = "0.0.0.0"
    return local_ip


def get_local_ip_os():
    try:
        operating_system = platform.system()
        if operating_system == "Windows":
            command = "ipconfig"
            result = os.popen(command).read()
            # Look for the line that contains the IP address
            for line in result.split('\n'):
                if "IPv4 Address" in line:
                    return line.split(': ')[1]
        elif operating_system in ["Linux", "Darwin"]:  # Darwin is macOS
            command = "ifconfig"
            result = os.popen(command).read()
            # This will grab the first IP address returned by ifconfig
            import re
            pattern = r'inet (\d+\.\d+\.\d+\.\d+)'
            match = re.search(pattern, result)
            if match:
                return match.group(1)
    except Exception as e:
        # return "Unable to determine local IP: " + str(e)
        return "0.0.0.0"

    return "0.0.0.0"


async def get_public_ip_async():
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get('https://www.ip-details.com/ip') as response:
                data = await response.text()
                return data
        except Exception as e:
            pass
        try:
            async with session.get('https://httpbin.org/ip') as response:
                data = await response.json()
                return data['origin']
        except Exception as e:
            pass
        
    return "0.0.0.0"


def get_public_ip():
    return asyncio.run(get_public_ip_async())
        

def get_local_ip():
    ip = get_local_ip_socket()
    if ip == "0.0.0.0":
        return get_local_ip_os()
    else:
        return ip


def get_hostname():
    ip = get_hostname_socket()
    if ip == "0.0.0.0":
        return get_hostname_os()
    else:
        return ip