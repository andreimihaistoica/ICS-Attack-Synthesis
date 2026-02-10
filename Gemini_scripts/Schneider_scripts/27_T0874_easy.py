import sys
import os
import time
import ctypes
import struct
import psutil  # For process enumeration (install with `pip install psutil`)
from scapy.all import * # For network discovery
from threading import Thread

# --- Configuration ---
TARGET_PROCESS_NAME = "ExecutableName.exe"  # Replace with the target process name (e.g., "opcua_client.exe")
TARGET_DLL_NAME = "ws2_32.dll"  # Replace with the target DLL (e.g., "ws2_32.dll" for network functions)
TARGET_API_FUNCTION_NAME = "send"  # Replace with the target API function (e.g., "send")
PLC_IP_ADDRESS = None  # PLC IP Address (will be discovered or manually entered)
COMMUNICATION_TECHNOLOGY = 'modbus' #communication protocol (modbus, opcua)

# --- Helper Functions ---

def find_process_id(process_name):
    """Finds the process ID (PID) of a process by its name."""
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'].lower() == process_name.lower():
            return process.info['pid']
    return None

def get_module_base_address(pid, module_name):
    """Gets the base address of a loaded module (DLL) in a process."""
    try:
        process = psutil.Process(pid)
        for module in process.memory_maps():
            if module.path and os.path.basename(module.path).lower() == module_name.lower():
                return module.addr
        return None
    except psutil.NoSuchProcess:
        return None

def read_memory(pid, address, size):
    """Reads memory from a process."""
    try:
        process_handle = ctypes.windll.kernel32.OpenProcess(
            0x1F0FFF,  # PROCESS_ALL_ACCESS (be careful!)
            False,
            pid
        )
        if process_handle:
            buffer = ctypes.create_string_buffer(size)
            bytes_read = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.ReadProcessMemory(
                process_handle,
                address,
                buffer,
                size,
                ctypes.byref(bytes_read)
            )
            ctypes.windll.kernel32.CloseHandle(process_handle)
            return buffer.raw
        else:
            print(f"Error: Could not open process (PID: {pid})")
            return None
    except Exception as e:
        print(f"Error reading memory: {e}")
        return None

def write_memory(pid, address, data):
    """Writes memory to a process."""
    try:
        process_handle = ctypes.windll.kernel32.OpenProcess(
            0x1F0FFF,  # PROCESS_ALL_ACCESS
            False,
            pid
        )
        if process_handle:
            bytes_written = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.WriteProcessMemory(
                process_handle,
                address,
                data,
                len(data),
                ctypes.byref(bytes_written)
            )
            ctypes.windll.kernel32.CloseHandle(process_handle)
            return True
        else:
            print(f"Error: Could not open process (PID: {pid}) for writing")
            return False
    except Exception as e:
        print(f"Error writing memory: {e}")
        return False

def find_iat_entry(pid, module_base_address, function_name):
    """Locates the IAT entry for a given function in a module."""
    # This is a simplified approach. A robust IAT search requires parsing the PE header.
    # This may need adjustments based on the target executable's structure.

    # Iterate through potential IAT entries (adjust the range based on the module size)
    for offset in range(0x1000, 0x4000, 4):  # Check every 4 bytes (32-bit) or 8 bytes (64-bit)
        iat_entry_address = module_base_address + offset
        try:
            # Read the address at the IAT entry
            data = read_memory(pid, iat_entry_address, 4)  # Assuming 32-bit
            if not data:
                continue

            function_address = struct.unpack("<I", data)[0]  # Unpack as unsigned int (32-bit)

            # Try to read some bytes from the function address to see if it looks like code
            function_bytes = read_memory(pid, function_address, 16)
            if function_bytes:
                # Check for common instruction prefixes (e.g., 0x55 = push ebp, 0x48 = REX.W for 64-bit)
                if function_bytes.startswith(b'\x55') or function_bytes.startswith(b'\x48'):  # Basic heuristic
                    #Try to resolve the address to a function name.

                    try:
                        ctypes.windll.kernel32.GetProcAddress.restype = ctypes.c_void_p
                        h_module = ctypes.windll.kernel32.LoadLibraryA(TARGET_DLL_NAME.encode('ascii'))
                        func_address_check = ctypes.windll.kernel32.GetProcAddress(h_module, function_name.encode('ascii'))

                        if (func_address_check == function_address):
                            return iat_entry_address

                    except Exception as e:
                        continue #print("Failed to resolve " + str(function_address) + " " + str(e))

        except Exception as e:
            #print(f"Error reading IAT entry at {hex(iat_entry_address)}: {e}")
            continue

    return None

# --- PLC Discovery Functions ---

def discover_plc_ip_address(technology):
    """
    Attempts to automatically discover the PLC's IP address.

    Args:
        technology (str): The communication technology used (e.g., "modbus", "opcua").
    """
    global PLC_IP_ADDRESS

    if technology.lower() == "modbus":
        PLC_IP_ADDRESS = discover_modbus_plc_ip()
    elif technology.lower() == "opcua":
        # Implement OPC UA discovery (requires OPC UA libraries)
        print("OPC UA discovery not yet implemented. Please enter the PLC IP address manually.")
        PLC_IP_ADDRESS = input("Enter PLC IP address: ")
    else:
        print("Unsupported communication technology. Please enter the PLC IP address manually.")
        PLC_IP_ADDRESS = input("Enter PLC IP address: ")

    if not PLC_IP_ADDRESS:
        PLC_IP_ADDRESS = input("Could not automatically discover PLC IP address. Please enter it manually: ")

def discover_modbus_plc_ip():
    """
    Discovers Modbus devices on the local network.

    This function sends Modbus/TCP queries to the broadcast address and listens for responses.
    It requires root/administrator privileges to send raw packets.
    """
    print("Attempting to discover Modbus PLC IP address...")

    # Define Modbus/TCP query (function code 0x04: Read Input Registers, address 0, count 1)
    modbus_query = b'\x00\x01\x00\x00\x00\x06\x01\x04\x00\x00\x00\x01'

    # Craft the TCP/IP packet
    ip = IP(dst="255.255.255.255")  # Broadcast address
    tcp = TCP(dport=502)  # Standard Modbus port

    packet = ip/tcp/modbus_query

    # Send the packet and capture responses
    responses = sr(packet, timeout=2, verbose=False)

    if responses and responses.res:
        for sent, received in responses.res:
            if IP in received:
                plc_ip = received[IP].src
                print(f"Found Modbus PLC at IP address: {plc_ip}")
                return plc_ip
    else:
        print("No Modbus PLC found on the network.")
        return None


# --- IAT Hooking Function ---
original_function = None

def iat_hook(process_name, dll_name, function_name):
    """Hooks an API function in a target process using IAT hooking."""
    global original_function

    pid = find_process_id(process_name)
    if not pid:
        print(f"Error: Process '{process_name}' not found.")
        return False

    module_base_address = get_module_base_address(pid, dll_name)
    if not module_base_address:
        print(f"Error: Module '{dll_name}' not found in process '{process_name}'.")
        return False

    iat_entry_address = find_iat_entry(pid, module_base_address, function_name)
    if not iat_entry_address:
        print(f"Error: IAT entry for function '{function_name}' not found in module '{dll_name}'.")
        return False

    print(f"Target Process ID: {pid}")
    print(f"Module Base Address: {hex(module_base_address)}")
    print(f"IAT Entry Address: {hex(iat_entry_address)}")


    # 1. Read the original function address from the IAT
    original_function_address_bytes = read_memory(pid, iat_entry_address, 4) # Assuming 32-bit
    if not original_function_address_bytes:
        print("Error: Could not read original function address from IAT.")
        return False

    original_function_address = struct.unpack("<I", original_function_address_bytes)[0]

    print(f"Original {function_name} function address: {hex(original_function_address)}")

    # 2. Define the detour function (the hook)
    # Define the function prototype based on the hooked API (example for 'send')
    # You'll need to adjust this based on the actual API function's arguments and return type.

    if (function_name == "send"):
        original_function_type = ctypes.WINFUNCTYPE(
            ctypes.c_int,
            ctypes.c_int,  # SOCKET s
            ctypes.c_char_p,  # const char *buf
            ctypes.c_int,  # int len
            ctypes.c_int   # int flags
        )

        def detour_function(s, buf, length, flags):
            """Detour function for the 'send' API."""
            try:
                # Log the parameters
                data = buf[:length]
                print(f"[Hooked send] Socket: {s}, Length: {length}, Flags: {flags}")

                # Log data being sent (attempt to decode as ASCII)
                try:
                    print(f"[Hooked send] Data: {data.decode('ascii')}")
                except UnicodeDecodeError:
                    print(f"[Hooked send] Data (raw): {data}")

                #Implement communication protocol parsing (Modbus)
                if (COMMUNICATION_TECHNOLOGY == 'modbus'):
                    parse_modbus_packet(data)

                #Optionally modify the data here before sending it.
                #modified_data = b"Modified data!"
                #length = len(modified_data)
                #return original_function(s, modified_data, length, flags)

                # Call the original function
                result = original_function(s, buf, length, flags)
                return result
            except Exception as e:
                print(f"Error in detour function: {e}")
                return -1  # Or an appropriate error code

        # Convert the detour function to a ctypes function
        detour_function_ptr = original_function_type(detour_function)
    else:
        print("No detour function prototype found. Exiting")
        return False

    # 3. Write the address of the detour function to the IAT entry
    detour_function_address = ctypes.addressof(detour_function_ptr)
    detour_function_address_bytes = struct.pack("<I", detour_function_address) #pack as 32 bit int

    print(f"Detour function address: {hex(detour_function_address)}")

    if not write_memory(pid, iat_entry_address, detour_function_address_bytes):
        print("Error: Could not write detour function address to IAT.")
        return False

    #Save a reference to the original function for use in the detour
    original_function = original_function_type(original_function_address)

    print(f"IAT Hook installed for '{function_name}' in process '{process_name}'.")
    return True


def parse_modbus_packet(data):
    """Parses and prints information from a Modbus packet."""
    try:
        transaction_id = struct.unpack(">H", data[0:2])[0]
        protocol_id = struct.unpack(">H", data[2:4])[0]
        length = struct.unpack(">H", data[4:6])[0]
        unit_id = data[6]
        function_code = data[7]

        print(f"[Modbus] Transaction ID: {transaction_id}")
        print(f"[Modbus] Protocol ID: {protocol_id}")
        print(f"[Modbus] Length: {length}")
        print(f"[Modbus] Unit ID: {unit_id}")
        print(f"[Modbus] Function Code: {function_code}")

        # Add more parsing logic based on the function code (e.g., read/write registers)
    except Exception as e:
        print(f"Error parsing Modbus packet: {e}")


# --- Main ---
def main():
    global PLC_IP_ADDRESS

    # 1. PLC Discovery (optional)
    discover_plc_ip_address(COMMUNICATION_TECHNOLOGY)

    if PLC_IP_ADDRESS:
        print(f"PLC IP Address: {PLC_IP_ADDRESS}")
    else:
        print("PLC IP address not found.  Continuing without it.")

    # 2. IAT Hooking
    if iat_hook(TARGET_PROCESS_NAME, TARGET_DLL_NAME, TARGET_API_FUNCTION_NAME):
        print("IAT Hooking successful.  Monitoring the target process...")
        # Keep the script running to maintain the hook
        while True:
            time.sleep(1)
    else:
        print("IAT Hooking failed.")

if __name__ == "__main__":
    if os.name != 'nt':
        print("This script is designed for Windows.")
        sys.exit(1)

    if not os.geteuid() == 0:
        print("Please run this script with administrator privileges.")
        sys.exit(1)

    main()