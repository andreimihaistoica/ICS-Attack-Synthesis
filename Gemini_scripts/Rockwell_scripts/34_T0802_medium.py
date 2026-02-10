import opcua
import socket
import subprocess
import time
import os

# Configuration
OPC_SERVER_IP = None  # Will be discovered
OPC_SERVER_PORT = 4840  # Default OPC UA port
NAMESPACE_INDEX = 2  # Namespace of the Micro850 (adjust if needed)
VARIABLES_TO_COLLECT = [
    "Controller.DateTime",
    "Controller.Program:MainProgram.Counter",  # Example: Replace with actual variables
    "Controller.Program:MainProgram.Temperature"  # Example: Replace with actual variables
]

OUTPUT_FILE = "ics_data_collection.txt"  # File to store collected data
LOG_FILE = "opcua_scan_log.txt" # For logging IP discovery attempts

def find_plc_ip():
    """
    Attempts to discover the PLC's IP address.
    This function uses various methods like pinging a broadcast address,
    scanning the network using nmap (if available), or reading the ARP cache.

    Returns:
        str: The PLC's IP address if found, otherwise None.
    """
    print("Attempting to discover the PLC's IP address...")

    # Method 1: Ping broadcast address (requires appropriate network configuration)
    # This approach is unreliable and often blocked by default firewall rules.
    # If your network allows broadcast pings, uncomment the following code:
    #
    # try:
    #     broadcast_address = "192.168.1.255" # Replace with your network's broadcast address. Important!
    #     response = os.system(f"ping -c 1 {broadcast_address} > /dev/null 2>&1") # Linux/macOS
    #     #response = os.system(f"ping -n 1 {broadcast_address} > nul 2>&1") # Windows
    #     if response == 0:
    #         print(f"Broadcast ping successful.  Check ARP cache for IPs: {broadcast_address}")
    #         # Parse ARP cache
    #         try:
    #             arp_output = subprocess.check_output(["arp", "-a"]).decode("utf-8")
    #             for line in arp_output.splitlines():
    #                 if "incomplete" not in line and "ff:ff:ff:ff:ff:ff" not in line:  # Filter out incomplete entries and broadcast MAC
    #                     ip = line.split()[1].strip("()")
    #                     print(f"Found IP address from ARP cache: {ip}")
    #                     return ip  # Return the first valid IP found
    #         except Exception as e:
    #             print(f"Error parsing ARP cache: {e}")
    #
    # except Exception as e:
    #     print(f"Broadcast Ping Failed (or requires root/admin access): {e}")


    # Method 2: Use nmap (if installed).
    try:
        # Determine operating system
        if os.name == 'nt': # Windows
            nmap_command = ["nmap", "-sn", "192.168.1.0/24"]  # Replace with your network range
        else: # Linux, macOS
            nmap_command = ["sudo", "nmap", "-sn", "192.168.1.0/24"]  # Replace with your network range, sudo needed usually.
        
        nmap_output = subprocess.check_output(nmap_command).decode("utf-8")
        with open(LOG_FILE, "a") as log:
            log.write(f"Nmap Output: {nmap_output}\n")
        for line in nmap_output.splitlines():
            if "Nmap scan report for" in line:
                ip = line.split(" ")[-1]
                print(f"Found potential PLC IP using nmap: {ip}")
                # Basic validation. You'll need to refine this.
                #  PLC manufacturers often use specific prefixes, so check for those here!
                if ip.startswith("192.168."): #Example
                  print(f"IP Address {ip} found")
                  return ip
                else:
                   print(f"Ignoring {ip} (doesn't match expected pattern)")

    except FileNotFoundError:
        print("nmap is not installed. Please install nmap or use another discovery method.")
        with open(LOG_FILE, "a") as log:
            log.write("Nmap not installed.  Please install and rerun.\n")

    except Exception as e:
        print(f"Error running nmap: {e}")
        with open(LOG_FILE, "a") as log:
            log.write(f"Nmap Failed: {e}\n")

    # Method 3:  Iterate through a potential IP range
    # Least reliable, but avoids external dependencies
    for i in range(1, 255):
        potential_ip = f"192.168.1.{i}" # Replace with your base network address
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)  # Short timeout to avoid long delays
            result = sock.connect_ex((potential_ip, OPC_SERVER_PORT)) # Connect to port 4840 to check if OPC UA is active
            if result == 0:
                print(f"Found potential PLC IP by connect: {potential_ip}")
                return potential_ip
            sock.close()
        except Exception as e:
            pass #Ignore errors during scan
    print("Failed to discover PLC IP address.")
    with open(LOG_FILE, "a") as log:
            log.write("IP Discovery Failed completely.\n")

    return None


def collect_data(opc_server_ip, variables):
    """
    Connects to the OPC UA server, reads the specified variables,
    and saves the data to a file.

    Args:
        opc_server_ip (str): The IP address of the OPC UA server.
        variables (list): A list of OPC UA variable node IDs to collect.
    """
    try:
        client = opcua.Client(f"opc.tcp://{opc_server_ip}:{OPC_SERVER_PORT}")
        client.connect()
        print(f"Connected to OPC UA server at {opc_server_ip}")

        with open(OUTPUT_FILE, "a") as f:  # Append to the file
            f.write(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            for variable_name in variables:
                try:
                    node_id = f"ns={NAMESPACE_INDEX};s={variable_name}"
                    node = client.get_node(node_id)
                    value = node.get_value()
                    f.write(f"  {variable_name}: {value}\n")
                    print(f"  {variable_name}: {value}")

                except opcua.ua.uaerrors.BadNodeIdUnknown as e:
                    print(f"  Error: Node ID '{variable_name}' not found.  Check NAMESPACE_INDEX and variable name. Error: {e}")
                    f.write(f"  Error: Node ID '{variable_name}' not found.  Check NAMESPACE_INDEX and variable name. Error: {e}\n")
                except Exception as e:
                    print(f"  Error reading variable '{variable_name}': {e}")
                    f.write(f"  Error reading variable '{variable_name}': {e}\n")


            f.write("\n")  # Add a blank line between data collections
            print("Data collection complete.")

        client.disconnect()
        print("Disconnected from OPC UA server.")

    except opcua.ua.uaerrors.BadServerUriInvalid as e:
        print(f"Error connecting to OPC UA server (Invalid URI): {e}. Check the OPC_SERVER_IP and OPC_SERVER_PORT.")
    except ConnectionRefusedError as e:
        print(f"Error connecting to OPC UA server (Connection Refused): {e}.  Ensure the PLC OPC UA server is running and reachable.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    # 1.  Find the PLC's IP Address
    OPC_SERVER_IP = find_plc_ip()

    if OPC_SERVER_IP:
        print(f"PLC IP Address found: {OPC_SERVER_IP}")
        # 2. Collect Data from PLC using OPC UA.
        collect_data(OPC_SERVER_IP, VARIABLES_TO_COLLECT)
    else:
        print("Could not determine PLC IP address.  Exiting.")