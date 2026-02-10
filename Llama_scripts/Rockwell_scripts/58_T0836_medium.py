import subprocess
from scapy.all import *
import time
import threading
from pycomm import CIP

# Define the subnet to scan
subnet = '192.168.1.0/24'

def find_plc_ip(subnet):
    try:
        output = subprocess.check_output(['nmap', '-sP', subnet]).decode('utf-8')
        for line in output.split('\n'):
            if 'Micro850' in line:  
                ip_address = line.split(' ')[-1]
                return ip_address
    except Exception as e:
        print(f"Failed to find PLC IP: {e}")
        return None

def modify_parameter(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Get the list of parameters
        parameters = cip_client.get_parameters()
        
        # Print the list of parameters
        print("Parameters:")
        print(parameters)
        
        # Modify a parameter
        # For example, modify the total number of seconds to run a motor
        parameter_name = "Motor_Run_Time"  # Replace with the actual parameter name
        new_value = 3600  # Replace with the new value
        cip_client.set_parameter(parameter_name, new_value)
        
        # Or, modify multiple parameters
        parameters_to_modify = {
            "Motor_Run_Time": 3600,
            "Motor_Speed": 100
        }
        cip_client.set_parameters(parameters_to_modify)
        
        print("Parameter modified successfully")
    except Exception as e:
        print(f"Failed to modify parameter: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        while True:
            print("1. Modify Parameter")
            print("2. Exit")
            choice = input("Enter your choice: ")
            
            if choice == "1":
                modify_parameter(plc_ip)
            elif choice == "2":
                break
            else:
                print("Invalid choice. Please try again.")
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()