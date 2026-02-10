import socket
import struct
import sys
from opcua import Client

# Function to find PLC IP in the local network
def find_plc_ip(subnet="192.168.1."):
    """
    Scans the local subnet to find a reachable OPC UA server (PLC).
    """
    for i in range(1, 255):
        ip = f"{subnet}{i}"
        try:
            # Try connecting to the common OPC UA port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)  # Timeout for responsiveness
            result = sock.connect_ex((ip, 4840))  # OPC UA default port
            
            if result == 0:
                print(f"[+] Found possible PLC at {ip}")
                return ip  # Return first detected PLC IP
            
            sock.close()
        except Exception as e:
            continue
    print("[-] No PLC found on the network.")
    sys.exit(1)

# Function to connect to PLC and collect data
def collect_data(plc_ip):
    """
    Connects to the PLC using OPC UA and retrieves node information.
    """
    url = f"opc.tcp://{plc_ip}:4840"
    print(f"[+] Connecting to PLC at {url}...")

    try:
        client = Client(url)
        client.connect()
        
        print("[+] Connected successfully.")
        
        # Get root node
        root = client.get_root_node()
        print(f"[+] Root node: {root}")

        # Browse the PLC available nodes
        objects = client.get_objects_node()
        print("[+] Available objects:")
        for node in objects.get_children():
            print(f" - {node} | BrowseName: {node.get_browse_name()}")

        # Collect specific data (Modify depending on the available nodes)
        vars = objects.get_variables()
        for var in vars:
            print(f"[+] Variable: {var.get_browse_name()} = {var.get_value()}")

        client.disconnect()
    
    except Exception as e:
        print(f"[-] Error communicating with PLC: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    print("[*] Beginning discovery process...")
    plc_ip = find_plc_ip()  # Step 1: Find the PLC's IP
    print(f"[+] PLC found at {plc_ip}")

    print("[*] Attempting to collect data from the PLC...")
    collect_data(plc_ip)  # Step 2: Collect PLC data