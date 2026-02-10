import os
import sys
import ctypes
import psutil
import socket
from ctypes import wintypes
from ctypes import windll

# Constants
PROCESS_ALL_ACCESS = 0x1F0FFF

# Find PLC's IP address
def find_plc_ip():
    for interface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == socket.AF_INET and not addr.address.startswith('127.'):
                print(f"Found IP address: {addr.address} on interface {interface}")
                return addr.address
    return None

# Hook function to replace the original API function
def hook_function(process_handle, original_function, new_function):
    # Get the base address of the module containing the original function
    module_handle = windll.kernel32.GetModuleHandleA(None)
    if module_handle == 0:
        print("Failed to get module handle.")
        return False

    # Get the address of the original function
    original_address = windll.kernel32.GetProcAddress(module_handle, original_function.encode())
    if original_address == 0:
        print(f"Failed to get address of {original_function}.")
        return False

    # Write the address of the new function to the IAT
    written = ctypes.c_size_t(0)
    result = windll.kernel32.WriteProcessMemory(process_handle, original_address, ctypes.byref(ctypes.cast(new_function, ctypes.c_void_p)), ctypes.sizeof(ctypes.c_void_p), ctypes.byref(written))
    if result == 0:
        print("Failed to write to process memory.")
        return False

    print(f"Hooked {original_function} successfully.")
    return True

# Example new function to replace the original API function
def new_message_box(hwnd, text, caption, utype):
    print("Hooked MessageBoxA function called!")
    return 0

# Main function
def main():
    # Find PLC's IP address
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"PLC IP address: {plc_ip}")
    else:
        print("Could not find PLC IP address.")

    # Target process ID (replace with the actual PID of the target process)
    target_pid = int(input("Enter the target process ID: "))

    # Open the target process
    process_handle = windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, target_pid)
    if process_handle == 0:
        print("Failed to open target process.")
        return

    # Hook the MessageBoxA function
    if hook_function(process_handle, "MessageBoxA", new_message_box):
        print("Hooking successful!")
    else:
        print("Hooking failed.")

    # Clean up
    windll.kernel32.CloseHandle(process_handle)

if __name__ == "__main__":
    main()