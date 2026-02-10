import ctypes
import socket
import sys
from ctypes import wintypes
from ctypes import windll, byref, Structure, POINTER, c_void_p, sizeof
from ctypes.wintypes import DWORD, HANDLE, HMODULE, LPVOID, LPCSTR, LPSTR, LPCWSTR, WORD, BYTE

# Constants for Windows API
PROCESS_ALL_ACCESS = 0x1F0FFF
PAGE_EXECUTE_READWRITE = 0x40

# Structures for Windows API
class MODULEINFO(Structure):
    _fields_ = [
        ("lpBaseOfDll", LPVOID),
        ("SizeOfImage", DWORD),
        ("EntryPoint", LPVOID),
    ]

# Function pointers for Windows API
kernel32 = windll.kernel32
psapi = windll.psapi

# Find the PLC's IP address
def find_plc_ip():
    ip_range = "192.168.9."
    for i in range(1, 255):
        ip = ip_range + str(i)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)
                s.connect((ip, 502))  # Modbus TCP port
                print(f"Found PLC at IP: {ip}")
                return ip
        except:
            continue
    print("PLC not found in the network.")
    return None

# IAT Hooking function
def iat_hook(process_handle, module_name, function_name, hook_function):
    # Get module handle
    module_handle = kernel32.GetModuleHandleA(module_name.encode())
    if not module_handle:
        print(f"Module {module_name} not found.")
        return False

    # Get function address
    function_address = kernel32.GetProcAddress(module_handle, function_name.encode())
    if not function_address:
        print(f"Function {function_name} not found.")
        return False

    # Allocate memory for the hook
    hook_code = ctypes.create_string_buffer(5)
    hook_code[0] = 0xE9  # JMP instruction
    ctypes.cast(ctypes.addressof(hook_code) + 1, POINTER(ctypes.c_uint32)).contents.value = (
        ctypes.cast(hook_function, ctypes.c_uint32).value - function_address - 5
    )

    # Write the hook
    kernel32.WriteProcessMemory(process_handle, function_address, hook_code, 5, None)
    print(f"Hooked {function_name} in {module_name}.")
    return True

# Example hook function
def my_hook_function():
    print("Hooked function executed!")

# Main function
if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if not plc_ip:
        sys.exit("Could not find PLC IP address.")

    # Example: Hook MessageBoxA in user32.dll
    process_handle = kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, kernel32.GetCurrentProcessId())
    if not process_handle:
        sys.exit("Failed to open process.")

    if iat_hook(process_handle, "user32.dll", "MessageBoxA", my_hook_function):
        print("IAT hooking successful.")
    else:
        print("IAT hooking failed.")

    kernel32.CloseHandle(process_handle)