import subprocess
from scapy.all import *
import time
import threading
from pycomm import CIP
import opcua

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

def automate_collection(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Use OPC-UA to collect information from the PLC
        client = opcua.Client(f"opc.tcp://{plc_ip}:4840/")
        client.connect()
        print("Connected to OPC-UA server")
        
        # Get the namespace array
        namespace_array = client.get_namespace_array()
        print(f"Namespace array: {namespace_array}")
        
        # Get the node list
        node_list = client.get_node_list()
        print(f"Node list: {node_list}")
        
        # Get the variable list
        variable_list = client.get_variable_list()
        print(f"Variable list: {variable_list}")
        
        client.disconnect()
        print("Disconnected from OPC-UA server")
        
        print(f"Automated collection completed on PLC: {plc_ip}")
    except Exception as e:
        print(f"Failed to automate collection: {e}")

def enumerate_devices(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Use CIP to enumerate devices connected to the PLC
        device_list = cip_client.get_device_list()
        print(f"Device list: {device_list}")
        
        print(f"Device enumeration completed on PLC: {plc_ip}")
    except Exception as e:
        print(f"Failed to enumerate devices: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        # Automate collection of industrial environment information
        automate_collection(plc_ip)
        
        # Enumerate devices connected to the PLC
        enumerate_devices(plc_ip)
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()