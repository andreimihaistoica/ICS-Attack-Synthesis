import socket
import struct
import time
import ipaddress
from threading import Thread

# Function to scan the network for the PLC's IP address
def find_plc_ip(network_range="192.168.1.0/24", plc_port=502):
    network = ipaddress.ip_network(network_range)
    print(f"Scanning network {network_range} for PLC...")
    for ip in network.hosts():
        ip = str(ip)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)
                s.connect((ip, plc_port))
                print(f"PLC found at IP address: {ip}")
                return ip
        except:
            continue
    print("PLC not found on the network.")
    return None

# Function to modify a parameter on the PLC (e.g., motor runtime)
def modify_plc_parameter(plc_ip, plc_port=502, register_address=0, new_value=1000):
    try:
        # Create a Modbus TCP request to write to a holding register
        transaction_id = 1  # Random transaction ID
        protocol_id = 0      # Modbus protocol ID
        length = 6          # Length of the remaining bytes
        unit_id = 1          # Unit ID (PLC address)
        function_code = 6    # Function code 6: Write Single Register
        register_address = register_address  # Address of the register to modify
        new_value = new_value  # New value to write

        # Pack the Modbus TCP request
        request = struct.pack(">HHHBBHH", transaction_id, protocol_id, length, unit_id, function_code, register_address, new_value)

        # Send the request to the PLC
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((plc_ip, plc_port))
            s.send(request)

            # Receive the response
            response = s.recv(1024)
            if response:
                print(f"Parameter at register {register_address} modified to {new_value}.")
            else:
                print("Failed to modify parameter.")
    except Exception as e:
        print(f"Error modifying PLC parameter: {e}")

# Main script
if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    if not plc_ip:
        exit(1)

    # Step 2: Modify a critical parameter (e.g., motor runtime)
    print("Modifying PLC parameter...")
    modify_plc_parameter(plc_ip, register_address=0, new_value=9999)  # Example: Set motor runtime to 9999 seconds