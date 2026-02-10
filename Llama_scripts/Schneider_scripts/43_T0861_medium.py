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

def collect_point_and_tag_values(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Get the list of points
        points = cip_client.get_points()
        print(f"Points: {points}")
        
        # Get the list of tags
        tags = cip_client.get_tags()
        print(f"Tags: {tags}")
        
        # Map inputs, outputs, and other values to their control processes
        for point in points:
            tag = cip_client.get_tag(point)
            print(f"Point: {point}, Tag: {tag}")
        
        print(f"Point and tag value collection completed on PLC: {plc_ip}")
    except Exception as e:
        print(f"Failed to collect point and tag values: {e}")

def identify_process_environment(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Get the process environment information
        process_environment = cip_client.get_process_environment()
        print(f"Process Environment: {process_environment}")
        
        print(f"Process environment identification completed on PLC: {plc_ip}")
    except Exception as e:
        print(f"Failed to identify process environment: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        # Collect point and tag values
        collect_point_and_tag_values(plc_ip)
        
        # Identify the process environment
        identify_process_environment(plc_ip)
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()