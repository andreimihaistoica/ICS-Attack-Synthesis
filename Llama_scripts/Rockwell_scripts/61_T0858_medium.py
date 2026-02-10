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

def change_operating_mode(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Get the current operating mode
        current_mode = cip_client.get_operating_mode()
        
        # Print the current operating mode
        print(f"Current Operating Mode: {current_mode}")
        
        # Change the operating mode
        # For example, change to Program mode
        new_mode = "Program"
        cip_client.set_operating_mode(new_mode)
        
        # Or, change to Run mode
        new_mode = "Run"
        cip_client.set_operating_mode(new_mode)
        
        # Or, change to Remote mode
        new_mode = "Remote"
        cip_client.set_operating_mode(new_mode)
        
        # Or, change to Stop mode
        new_mode = "Stop"
        cip_client.set_operating_mode(new_mode)
        
        # Or, change to Reset mode
        new_mode = "Reset"
        cip_client.set_operating_mode(new_mode)
        
        # Or, change to Test/Monitor mode
        new_mode = "Test/Monitor"
        cip_client.set_operating_mode(new_mode)
        
        print(f"Operating Mode changed to {new_mode}")
    except Exception as e:
        print(f"Failed to change operating mode: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        while True:
            print("1. Change Operating Mode")
            print("2. Exit")
            choice = input("Enter your choice: ")
            
            if choice == "1":
                change_operating_mode(plc_ip)
            elif choice == "2":
                break
            else:
                print("Invalid choice. Please try again.")
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()