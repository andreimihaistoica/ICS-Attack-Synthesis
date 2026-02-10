import sys
import time
import socket
import psutil
import pefile  # Requires 'pefile' library (pip install pefile)
from detours import Detour  # Requires 'detours' library (pip install detours)


# --- 1. PLC IP Address Discovery (Simple Example) ---
def find_plc_ip():
    """
    Attempts to find the PLC IP address by scanning the local network.
    This is a VERY basic example and may not work in all network configurations.
    You might need to adapt it to your specific network setup.
    """
    try:
        # Get the local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Connect to a public DNS server (doesn't send data)
        local_ip = s.getsockname()[0]
        s.close()

        # Determine the network address (e.g., 192.168.1.0/24)
        network_address = ".".join(local_ip.split(".")[:-1]) + ".0"
        #print(f"Local IP: {local_ip}, Network Address: {network_address}")

        # Ping scan (very basic and may require elevated privileges)
        for i in range(1, 255):
            target_ip = network_address + "." + str(i)
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.1) # Timeout in seconds
                result = s.connect_ex((target_ip, 502)) # Modbus port 502 or common PLC ports

                if result == 0:  # Port is open (likely a PLC)
                    print(f"Found potential PLC at: {target_ip}")
                    s.close()
                    return target_ip
                s.close()
            except socket.error as e:
                pass # Ignore errors

    except Exception as e:
        print(f"Error during PLC IP discovery: {e}")
        return None

    return None # PLC not found


# --- 2. API Hooking Implementation ---
def hook_api(process_name, dll_name, api_name, hook_function):
    """
    Hooks a specific API function in a given process.

    Args:
        process_name: Name of the process to target (e.g., "EngineeringWorkstation.exe").
        dll_name: Name of the DLL containing the API function (e.g., "ws2_32.dll").
        api_name: Name of the API function to hook (e.g., "send").
        hook_function: The Python function that will act as the hook.
    """

    # Find the target process by name
    target_pid = None
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'].lower() == process_name.lower():
            target_pid = proc.info['pid']
            break

    if target_pid is None:
        print(f"Process '{process_name}' not found.")
        return

    print(f"Found process '{process_name}' with PID: {target_pid}")

    try:
        # Get the process handle
        process_handle = psutil.Process(target_pid).as_dict()['pid'] #this returns int

        # Locate the API function address in the target process's memory space
        pe = pefile.PE(psutil.Process(target_pid).exe()) # Get executable path
        for imp in pe.DIRECTORY_ENTRY_IMPORT:
                if imp.dll.decode().lower() == dll_name.lower(): # find dll
                    for func in imp.imports: # check for function import
                        if func.name.decode() == api_name.encode().decode():
                            api_address = psutil.Process(target_pid).memory_maps()[0].addr + func.address # find offset of function, add to base address
                            break
        print(f"Found address for {api_name} in {dll_name}: {hex(api_address)}")

        # Create the detour (hook)
        detour = Detour(api_address, hook_function)
        detour.enable()  # Enable the hook
        print(f"Successfully hooked {api_name} in {process_name}.")

    except Exception as e:
        print(f"Error hooking API: {e}")


# --- 3. Example Hook Function (Modify as needed) ---
def my_hooked_send(socket, buff, length, flags):
    """
    Example hook function for the 'send' API.  This function will be called
    whenever the target process calls 'send'.

    Args:
        socket: The socket descriptor.
        buff: The buffer containing the data to be sent.
        length: The length of the data to be sent.
        flags: Flags for the 'send' call.

    Returns:
        The return value of the original 'send' function.
    """
    try:
        data = buff.decode('utf-8', errors='ignore') # Decode the buffer (if possible)
        print(f"[HOOKED send] Sending data: {data}")
        print(f"[HOOKED send] Length: {length}, Flags: {flags}")


        # *** IMPORTANT ***
        # Call the original 'send' function to avoid breaking functionality.
        # You must use 'detour.original()' to call the original function.
        # Otherwise, you'll create an infinite loop.
        original_send = my_hooked_send.detour.original
        return original_send(socket, buff, length, flags)

    except Exception as e:
        print(f"[HOOKED send] Error: {e}")
        original_send = my_hooked_send.detour.original
        return original_send(socket, buff, length, flags) # Still call original function to avoid crashing


# --- 4. Main Execution ---
if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"PLC IP Address: {plc_ip}")
    else:
        print("Could not automatically determine PLC IP address.")

    # Set the target process, DLL, and API function
    target_process = "EngineeringWorkstation.exe"  # Change to the actual EWS executable name
    target_dll = "ws2_32.dll"  # Winsock DLL (for network communication)
    target_api = "send"       # Example: Hook the 'send' API call

    # Call the hook_api function to enable the hook
    hook_api(target_process, target_dll, target_api, my_hooked_send)

    print("API Hooking started.  The script will run until you interrupt it (Ctrl+C).")
    print("Make the Engineering Workstation communicate with the PLC to trigger the hook.")

    try:
        while True:
            time.sleep(1) # Keep the script running
    except KeyboardInterrupt:
        print("\nAPI Hooking stopped.")