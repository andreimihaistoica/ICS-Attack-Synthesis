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

def program_upload(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Check the operating mode of the PLC
        operating_mode = cip_client.get_operating_mode()
        if operating_mode!= "Stop":
            print("PLC is not in stop mode. Changing to stop mode.")
            cip_client.set_operating_mode("Stop")
        
        # Upload the program from the PLC
        program_name = "MyProgram"  # Replace with the actual program name
        cip_client.upload_program(program_name)
        
        print("Program uploaded successfully")
    except Exception as e:
        print(f"Failed to upload program: {e}")

def read_program(plc_ip, program_name):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Read the program from the PLC
        program_data = cip_client.read_program(program_name)
        
        print("Program data:")
        print(program_data)
    except Exception as e:
        print(f"Failed to read program: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        while True:
            print("1. Program Upload")
            print("2. Read Program")
            print("3. Exit")
            choice = input("Enter your choice: ")
            
            if choice == "1":
                program_upload(plc_ip)
            elif choice == "2":
                program_name = input("Enter the program name: ")
                read_program(plc_ip, program_name)
            elif choice == "3":
                break
            else:
                print("Invalid choice. Please try again.")
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()