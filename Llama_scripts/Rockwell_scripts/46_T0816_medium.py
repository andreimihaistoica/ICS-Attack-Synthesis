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

def restart_plc(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Restart the PLC
        cip_client.restart()
        
        print("PLC restarted successfully")
    except Exception as e:
        print(f"Failed to restart PLC: {e}")

def shutdown_plc(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Shutdown the PLC
        cip_client.shutdown()
        
        print("PLC shutdown successfully")
    except Exception as e:
        print(f"Failed to shutdown PLC: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        while True:
            print("1. Restart PLC")
            print("2. Shutdown PLC")
            print("3. Exit")
            choice = input("Enter your choice: ")
            
            if choice == "1":
                restart_plc(plc_ip)
            elif choice == "2":
                shutdown_plc(plc_ip)
            elif choice == "3":
                break
            else:
                print("Invalid choice. Please try again.")
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()