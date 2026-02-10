import socket
from snap7 import client
from snap7.util import *
from snap7.types import *

# Function to find PLC's IP address in the network
def find_plc_ip():
    # Replace with your network's IP range and port
    ip_range = "192.168.1."
    port = 102  # Default port for Siemens S7 PLCs

    for i in range(1, 255):
        ip = ip_range + str(i)
        try:
            # Try to connect to the PLC
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)  # Short timeout for scanning
            result = sock.connect_ex((ip, port))
            if result == 0:
                print(f"PLC found at IP: {ip}")
                return ip
            sock.close()
        except Exception as e:
            print(f"Error scanning {ip}: {e}")
    print("PLC not found in the network.")
    return None

# Function to upload program from PLC
def upload_program_from_plc(plc_ip):
    try:
        # Create a Snap7 client
        plc = client.Client()
        plc.connect(plc_ip, 0, 1)  # Connect to the PLC

        # Upload the program (example: upload block DB1)
        block_type = BlockType.DB  # Data Block
        block_num = 1  # Block number
        program_data = plc.upload(block_type, block_num)

        # Save the program to a file
        with open(f"PLC_Program_DB{block_num}.bin", "wb") as file:
            file.write(program_data)

        print(f"Program uploaded and saved as PLC_Program_DB{block_num}.bin")
        plc.disconnect()
    except Exception as e:
        print(f"Error uploading program: {e}")

# Main script
if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()

    if plc_ip:
        # Step 2: Upload the program from the PLC
        upload_program_from_plc(plc_ip)
    else:
        print("Cannot proceed without PLC's IP address.")