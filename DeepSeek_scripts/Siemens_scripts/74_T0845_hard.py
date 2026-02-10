import snap7
import snap7.client as c
from snap7.util import *
from snap7.types import *
import socket

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Broadcast a discovery packet (modify as needed for your network)
    broadcast_ip = "255.255.255.255"
    port = 102  # Default Siemens S7 port
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(b"DISCOVER_PLC", (broadcast_ip, port))
        print("Broadcasting discovery packet...")
        sock.settimeout(5)  # Wait for 5 seconds for a response
        data, addr = sock.recvfrom(1024)
        print(f"Discovered PLC at IP: {addr[0]}")
        return addr[0]
    except Exception as e:
        print(f"Failed to discover PLC: {e}")
        return None
    finally:
        sock.close()

# Function to upload the program from the PLC
def upload_program(plc_ip):
    try:
        # Create a Snap7 client
        client = c.Client()
        client.connect(plc_ip, 0, 1)  # Connect to the PLC (rack=0, slot=1)
        print(f"Connected to PLC at {plc_ip}")

        # Upload the program (block type: OB, DB, etc.)
        # Example: Uploading the first OB (Organization Block)
        block_type = snap7.types.BlockType.OB
        block_num = 1
        program_data = client.upload(block_type, block_num)
        print(f"Uploaded program block {block_type} {block_num}")

        # Save the uploaded program to a file
        with open(f"PLC_Program_OB{block_num}.bin", "wb") as f:
            f.write(program_data)
        print(f"Program saved to PLC_Program_OB{block_num}.bin")

        client.disconnect()
        print("Disconnected from PLC")
    except Exception as e:
        print(f"Failed to upload program: {e}")

# Main script
if __name__ == "__main__":
    plc_ip = discover_plc_ip()
    if plc_ip:
        upload_program(plc_ip)
    else:
        print("PLC IP address could not be discovered.")