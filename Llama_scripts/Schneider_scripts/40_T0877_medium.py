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

def capture_io_image(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Get the input image table
        input_image_table = cip_client.get_input_image_table()
        print(f"Input Image Table: {input_image_table}")
        
        # Get the output image table
        output_image_table = cip_client.get_output_image_table()
        print(f"Output Image Table: {output_image_table}")
        
        # Get the I/O image state
        io_image_state = cip_client.get_io_image_state()
        print(f"I/O Image State: {io_image_state}")
        
        print(f"I/O Image capture completed on PLC: {plc_ip}")
    except Exception as e:
        print(f"Failed to capture I/O Image: {e}")

def access_memory_regions(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Use the native API to access the memory regions directly
        memory_regions = cip_client.access_memory_regions()
        print(f"Memory Regions: {memory_regions}")
        
        print(f"Memory region access completed on PLC: {plc_ip}")
    except Exception as e:
        print(f"Failed to access memory regions: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        # Capture the I/O image of the PLC
        capture_io_image(plc_ip)
        
        # Access the memory regions directly
        access_memory_regions(plc_ip)
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()