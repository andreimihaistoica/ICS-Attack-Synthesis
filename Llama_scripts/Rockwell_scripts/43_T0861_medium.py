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
            if 'Micro850' in line:  
                ip_address = line.split(' ')[-1]
                return ip_address
    except Exception as e:
        print(f"Failed to find PLC IP: {e}")
        return None

def collect_point_tag_values(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Get the list of points (inputs, outputs, memory locations, etc.)
        points = cip_client.get_points()
        
        # Print the list of points
        print("Points:")
        for point in points:
            print(point)
        
        # Get the list of tags (identifiers given to points for operator convenience)
        tags = cip_client.get_tags()
        
        # Print the list of tags
        print("Tags:")
        for tag in tags:
            print(tag)
        
        # Collect point and tag values
        point_tag_values = {}
        for point in points:
            tag = cip_client.get_tag(point)
            value = cip_client.get_value(point)
            point_tag_values[point] = {"tag": tag, "value": value}
        
        # Print the point and tag values
        print("Point and Tag Values:")
        for point, values in point_tag_values.items():
            print(f"Point: {point}, Tag: {values['tag']}, Value: {values['value']}")
    except Exception as e:
        print(f"Failed to collect point and tag values: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        # Collect point and tag values
        collect_point_tag_values(plc_ip)
        
        while True:
            user_input = input("Type 'top' to stop collecting point and tag values: ")
            if user_input.lower() == 'top':
                break
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()