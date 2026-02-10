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

def modify_alarm_settings(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Get the current alarm settings
        alarm_settings = cip_client.get_alarm_settings()
        
        # Print the current alarm settings
        print("Current Alarm Settings:")
        print(alarm_settings)
        
        # Modify the alarm settings
        # For example, disable all alarms
        cip_client.set_alarm_settings({"enabled": False})
        
        # Or, modify specific alarm settings
        # For example, change the alarm threshold for a specific tag
        tag = "MyTag"
        threshold = 10
        cip_client.set_alarm_threshold(tag, threshold)
        
        print("Alarm settings modified successfully")
    except Exception as e:
        print(f"Failed to modify alarm settings: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        while True:
            print("1. Modify Alarm Settings")
            print("2. Exit")
            choice = input("Enter your choice: ")
            
            if choice == "1":
                modify_alarm_settings(plc_ip)
            elif choice == "2":
                break
            else:
                print("Invalid choice. Please try again.")
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()