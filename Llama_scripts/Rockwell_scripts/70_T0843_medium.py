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

def program_download(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Check the operating mode of the PLC
        operating_mode = cip_client.get_operating_mode()
        if operating_mode!= "Program":
            print("PLC is not in program mode. Changing to program mode.")
            cip_client.set_operating_mode("Program")
        
        # Perform a program download
        program_name = "MyProgram"  # Replace with the actual program name
        cip_client.download_program(program_name)
        
        print("Program downloaded successfully")
    except Exception as e:
        print(f"Failed to download program: {e}")

def online_edit(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Check the operating mode of the PLC
        operating_mode = cip_client.get_operating_mode()
        if operating_mode!= "Run":
            print("PLC is not in run mode. Changing to run mode.")
            cip_client.set_operating_mode("Run")
        
        # Perform an online edit
        program_name = "MyProgram"  # Replace with the actual program name
        cip_client.online_edit(program_name)
        
        print("Online edit completed successfully")
    except Exception as e:
        print(f"Failed to perform online edit: {e}")

def program_append(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Check the operating mode of the PLC
        operating_mode = cip_client.get_operating_mode()
        if operating_mode!= "Run":
            print("PLC is not in run mode. Changing to run mode.")
            cip_client.set_operating_mode("Run")
        
        # Perform a program append
        program_name = "MyProgram"  # Replace with the actual program name
        cip_client.program_append(program_name)
        
        print("Program append completed successfully")
    except Exception as e:
        print(f"Failed to perform program append: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        while True:
            print("1. Program Download")
            print("2. Online Edit")
            print("3. Program Append")
            print("4. Exit")
            choice = input("Enter your choice: ")
            
            if choice == "1":
                program_download(plc_ip)
            elif choice == "2":
                online_edit(plc_ip)
            elif choice == "3":
                program_append(plc_ip)
            elif choice == "4":
                break
            else:
                print("Invalid choice. Please try again.")
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()