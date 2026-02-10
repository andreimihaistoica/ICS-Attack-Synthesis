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

def activate_firmware_update_mode(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Activate firmware update mode
        cip_client.activate_firmware_update_mode()
        
        print("Firmware update mode activated successfully")
    except Exception as e:
        print(f"Failed to activate firmware update mode: {e}")

def deactivate_firmware_update_mode(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Deactivate firmware update mode
        cip_client.deactivate_firmware_update_mode()
        
        print("Firmware update mode deactivated successfully")
    except Exception as e:
        print(f"Failed to deactivate firmware update mode: {e}")

def check_firmware_update_mode(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Check firmware update mode
        mode = cip_client.check_firmware_update_mode()
        
        if mode:
            print("Firmware update mode is active")
        else:
            print("Firmware update mode is inactive")
    except Exception as e:
        print(f"Failed to check firmware update mode: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        while True:
            print("1. Activate Firmware Update Mode")
            print("2. Deactivate Firmware Update Mode")
            print("3. Check Firmware Update Mode")
            print("4. Exit")
            choice = input("Enter your choice: ")
            
            if choice == "1":
                activate_firmware_update_mode(plc_ip)
            elif choice == "2":
                deactivate_firmware_update_mode(plc_ip)
            elif choice == "3":
                check_firmware_update_mode(plc_ip)
            elif choice == "4":
                break
            else:
                print("Invalid choice. Please try again.")
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()