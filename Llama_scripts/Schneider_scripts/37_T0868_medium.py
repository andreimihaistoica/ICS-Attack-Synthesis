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

def detect_operating_mode(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Get the current operating mode
        operating_mode = cip_client.get_operating_mode()
        print(f"Current operating mode: {operating_mode}")
        
        if operating_mode == 'Program':
            print("PLC is in program mode. Changes can be made to the device's program.")
        elif operating_mode == 'Run':
            print("PLC is in run mode. Execution of the device's program is occurring.")
        elif operating_mode == 'Remote':
            print("PLC is in remote mode. Remote changes to the PLC's operation mode are allowed.")
        elif operating_mode == 'Stop':
            print("PLC is in stop mode. The PLC and program are stopped, and outputs are forced off.")
        elif operating_mode == 'Reset':
            print("PLC is in reset mode. Conditions on the PLC are reset to their original states.")
        elif operating_mode == 'Test/Monitor':
            print("PLC is in test/monitor mode. I/O is processed, and monitoring, force set, resets, and more are allowed.")
        else:
            print("Unknown operating mode.")
        
        print(f"Operating mode detection completed on PLC: {plc_ip}")
    except Exception as e:
        print(f"Failed to detect operating mode: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        # Detect the current operating mode of the PLC
        detect_operating_mode(plc_ip)
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()