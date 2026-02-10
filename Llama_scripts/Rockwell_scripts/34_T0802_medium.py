import subprocess
from scapy.all import *
import time
import threading
from pyopcuaclient import Client

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

def automated_collection(plc_ip):
    try:
        # Create an OPC client
        client = Client(f"opc.tcp://{plc_ip}:4840/")
        
        # Connect to the OPC server
        client.connect()
        
        # Get the list of available nodes
        nodes = client.get_nodes()
        
        # Print the list of available nodes
        print("Available nodes:")
        for node in nodes:
            print(node)
        
        # Get the value of a node
        node_id = "ns=2;i=1"
        value = client.get_value(node_id)
        
        # Print the value of the node
        print(f"Value of {node_id}: {value}")
    except Exception as e:
        print(f"Failed to automate collection: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        # Automate the collection of industrial environment information
        automated_collection(plc_ip)
        
        while True:
            user_input = input("Type 'top' to stop automated collection: ")
            if user_input.lower() == 'top':
                break
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()