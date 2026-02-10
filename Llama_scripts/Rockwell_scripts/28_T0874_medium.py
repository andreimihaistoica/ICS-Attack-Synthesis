import subprocess
from scapy.all import *
import time
import threading
import ctypes
import ctypes.wintypes

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

def hook_api_function(api_function_name, hook_function):
    try:
        # Get the handle to the DLL containing the API function
        dll_handle = ctypes.windll.kernel32.GetModuleHandleW('kernel32.dll')
        
        # Get the address of the API function
        api_function_address = ctypes.windll.kernel32.GetProcAddress(dll_handle, api_function_name)
        
        # Define the hook function
        def hook_function_prototype(api_function_address):
            # Call the original API function
            original_api_function = ctypes.WINFUNCTYPE(ctypes.c_int)(api_function_address)
            return original_api_function()
        
        # Create a hook function
        hook_function_address = ctypes.CFUNCTYPE(ctypes.c_int)(hook_function_prototype)
        
        # Hook the API function
        ctypes.windll.kernel32.SetWindowsHookExW(3, hook_function_address, dll_handle, 0)
        
        print(f"Hooked API function: {api_function_name}")
    except Exception as e:
        print(f"Failed to hook API function: {e}")

def main():
    plc_ip = find_plc_ip(subnet)
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
        
        # Define the API function to hook
        api_function_name = 'CreateProcessW'
        
        # Define the hook function
        def hook_function():
            print("Hooked CreateProcessW API function")
            # Call the original API function
            return ctypes.windll.kernel32.CreateProcessW(None, None, None, None, False, 0, None, None, None)
        
        # Hook the API function
        hook_api_function(api_function_name, hook_function)
        
        while True:
            user_input = input("Type 'top' to stop hooking: ")
            if user_input.lower() == 'top':
                break
    else:
        print("PLC not found.")

if __name__ == "__main__":
    main()