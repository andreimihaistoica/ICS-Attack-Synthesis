import os
import socket
import struct
import ctypes
import psutil
import subprocess

# Function to discover devices on the local network
def discover_s7_1200_plc():
    print("[*] Discovering the Siemens S7-1200 PLC on the local network...")
    local_ip = socket.gethostbyname(socket.gethostname())  # Get local IP address
    ip_parts = local_ip.split('.')[:-1]
    network_prefix = '.'.join(ip_parts)  # Example: '192.168.0'
    plc_ip = None

    for i in range(1, 255):
        test_ip = f"{network_prefix}.{i}"
        try:
            # Attempt to connect to port 102 (typical S7 communication port)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            sock.connect((test_ip, 102))
            print(f"[+] Found S7-1200 PLC at IP: {test_ip}")
            plc_ip = test_ip
            sock.close()
            break
        except:
            pass  # Ignore connection errors

    if plc_ip is None:
        print("[-] No PLC found on network.")
        exit(1)

    return plc_ip

# Function for demonstrating IAT Hooking
def hook_iat(target_process_name):
    print(f"[*] Attempting to hook API functions in process: {target_process_name}")

    # Find the process by name
    target_pid = None
    for proc in psutil.process_iter(attrs=['pid', 'name']):
        if proc.info['name'] == target_process_name:
            target_pid = proc.info['pid']
            break

    if target_pid is None:
        print(f"[-] Process '{target_process_name}' not found.")
        return

    print(f"[+] Found process '{target_process_name}' with PID: {target_pid}")

    # Open the process with required access rights
    PROCESS_ALL_ACCESS = 0x1F0FFF
    kernel32 = ctypes.windll.kernel32
    process_handle = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, target_pid)

    if not process_handle:
        print("[-] Unable to open process. Ensure the script has sufficient privileges.")
        return

    print(f"[+] Successfully opened process. Handle: {process_handle}")

    # Locate the base address of kernel32.dll in the target process
    h_kernel32 = kernel32.GetModuleHandleW("kernel32.dll")
    if not h_kernel32:
        print("[-] Failed to get handle for kernel32.dll.")
        return

    print(f"[+] Located kernel32.dll in process. Handle: {h_kernel32}")

    # Find the address of the Sleep function in kernel32.dll
    sleep_addr = kernel32.GetProcAddress(h_kernel32, b"Sleep")
    if not sleep_addr:
        print("[-] Failed to locate 'Sleep' function in kernel32.dll.")
        return

    print(f"[+] Found Sleep function at address: {hex(sleep_addr)}")

    # Modify the target process's Import Address Table (IAT)
    print("[*] Modifying the IAT for hooking... (simulated)")

    # In a real-world scenario, you would need to locate the specific IAT of the target PE, replace the address, etc.
    # Here, we demonstrate the idea without applying actual hooks for safety
    print("[+] Simulated hooking complete. (No actual changes were made.)")

    # Close the process handle
    kernel32.CloseHandle(process_handle)

# Main Execution Logic
if __name__ == "__main__":
    print("[*] Starting the Hooking Script...")
    
    # Step 1: Discover Siemens S7-1200 PLC
    plc_ip = discover_s7_1200_plc()
    print(f"[+] Proceeding with PLC IP: {plc_ip}")
    
    # Step 2: Hook into a target process
    target_process = "notepad.exe"  # Example target process, replace with your process
    hook_iat(target_process)