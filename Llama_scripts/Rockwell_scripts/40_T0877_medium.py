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

def collect_io_image(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Get the I/O image state of the PLC
        io_image = cip_client.get_io_image()
        
        # Print the I/O image state
        print("I/O Image State:")
        print(io_image)
        
        # Collect the input and output image tables
        input_image_table = cip_client.get_input_image_table()
        output_image_table = cip_client.get_output_image_table()
        
        # Print the input and output image tables
        print("Input Image Table:")
        print(input_image_table)
        print("Output Image Table:")
        print(output_image_table)
    except Exception as e:
        print(f"Failed to collect I/O image: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        # Collect the I/O image state of the PLC
        collect_io_image(plc_ip)
        
        while True:
            user_input = input("Type 'top' to stop collecting I/O image: ")
            if user_input.lower() == 'top':
                break
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()