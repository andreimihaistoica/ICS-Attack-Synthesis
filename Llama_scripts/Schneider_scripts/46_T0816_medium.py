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

def restart_plc(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Restart the PLC
        cip_client.restart()
        print(f"PLC restarted: {plc_ip}")
    except Exception as e:
        print(f"Failed to restart PLC: {e}")

def shutdown_plc(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Shutdown the PLC
        cip_client.shutdown()
        print(f"PLC shutdown: {plc_ip}")
    except Exception as e:
        print(f"Failed to shutdown PLC: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        # Restart the PLC
        restart_plc(plc_ip)
        
        # Shutdown the PLC
        shutdown_plc(plc_ip)
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()