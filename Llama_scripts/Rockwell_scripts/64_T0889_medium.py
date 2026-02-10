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

def modify_program(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Get the list of programs on the PLC
        programs = cip_client.get_programs()
        
        # Print the list of programs
        print("Programs:")
        print(programs)
        
        # Modify a program
        # For example, add a new function to a program
        program_name = "MyProgram"  # Replace with the actual program name
        new_function = "MyNewFunction"  # Replace with the actual new function name
        cip_client.add_function(program_name, new_function)
        
        # Or, modify the logic in an existing function
        function_name = "MyFunction"  # Replace with the actual function name
        new_logic = "MyNewLogic"  # Replace with the actual new logic
        cip_client.modify_function(program_name, function_name, new_logic)
        
        # Or, make a new call from one function to another
        source_function = "MySourceFunction"  # Replace with the actual source function name
        destination_function = "MyDestinationFunction"  # Replace with the actual destination function name
        cip_client.add_call(program_name, source_function, destination_function)
        
        print("Program modified successfully")
    except Exception as e:
        print(f"Failed to modify program: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        while True:
            print("1. Modify Program")
            print("2. Exit")
            choice = input("Enter your choice: ")
            
            if choice == "1":
                modify_program(plc_ip)
            elif choice == "2":
                break
            else:
                print("Invalid choice. Please try again.")
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()