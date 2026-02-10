import ctypes
import socket
import struct
import os
from scapy.all import ARP, Ether, srp

# ==============================
# Step 1: Discover PLC's IP Address
# ==============================

def find_plc_ip(network="192.168.1.0/24"):
    """
    Scans the network for active devices and tries to identify a potential PLC.
    """
    print("[+] Scanning Network for PLC IP...")
    
    # Create an ARP request to identify devices on the subnet
    arp_request = ARP(pdst=network)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    devices = []
    for _, response in answered_list:
        devices.append(response.psrc)  # Collect IPs

    if devices:
        plc_ip = devices[0]  # Assuming the first device is the PLC
        print(f"[+] PLC identified at IP: {plc_ip}")
        return plc_ip
    else:
        print("[-] No PLC Found")
        return None

# ==============================
# Step 2: IAT Hooking on Windows
# ==============================

# Define function prototype for MessageBoxA
prototype = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_uint)

def hook_function(original_function):
    """
    Custom function that will replace the original one (hooked).
    """
    print("[+] Hooked function executed!")
    return 0  # Return value modified

def iat_hook():
    """
    Implements IAT Hooking on `MessageBoxA` function of user32.dll
    """
    print("[+] Executing IAT Hooking...")

    # Load user32.dll and find MessageBoxA
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32
    
    original_function_address = user32.MessageBoxA
    print(f"[+] Original function address: {hex(original_function_address)}")

    # Get the page where the function is stored
    page_start = struct.unpack("P", ctypes.string_at(ctypes.c_void_p(original_function_address), 8))[0] & ~0xFFF

    # Change memory permissions to allow writing
    old_protection = ctypes.c_ulong()
    kernel32.VirtualProtect(page_start, 4096, 0x40, ctypes.byref(old_protection))  # PAGE_EXECUTE_READWRITE

    # Replace the original function pointer with our hook
    hooked_function_pointer = prototype(hook_function)
    ctypes.memmove(original_function_address, ctypes.c_ulonglong(ctypes.addressof(hooked_function_pointer)), ctypes.sizeof(ctypes.c_void_p))

    print("[+] Successfully Hooked MessageBoxA!")

# ==============================
# Execution Flow
# ==============================

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        iat_hook()