import socket
import pycomm3
from pycomm3 import LogixDriver

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the broadcast address and port
    broadcast_address = '255.255.255.255'
    port = 44818  # Common port for EtherNet/IP

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Send a broadcast message to discover the PLC
    discovery_message = b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    sock.sendto(discovery_message, (broadcast_address, port))

    # Receive the response
    sock.settimeout(5)  # Set a timeout for the response
    try:
        data, addr = sock.recvfrom(1024)
        return addr[0]  # Return the IP address of the PLC
    except socket.timeout:
        print("No response from the PLC. Ensure the PLC is connected to the network.")
        return None
    finally:
        sock.close()

# Function to collect tag values from the PLC
def collect_tag_values(plc_ip):
    # List of tags to collect
    tags = [
        'NewVariable',
        'Activate_FanA',
        'FanA_Timer',
        'START',
        'STOP',
        'TON_1.IN',
        'TON_1.PT',
        'TON_1.Q',
        'TON_1.ET',
        'TON_1.Pdate',
        'TON_1.Redge',
        'TONOFF_1.IN',
        'TONOFF_1.PT',
        'TONOFF_1.PTOF',
        'TONOFF_1.Q',
        'TONOFF_1.ET',
        'TONOFF_1.PDATE',
        'TONOFF_1.REDGE',
        'TONOFF_1.FEDGE',
        'FanA_Off',
        'Tog_Off'
    ]

    # Connect to the PLC
    with LogixDriver(plc_ip) as plc:
        # Read the values of the tags
        tag_values = plc.read(*tags)

        # Print the collected tag values
        for tag in tag_values:
            print(f"{tag.tag_name}: {tag.value}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        print(f"PLC found at IP address: {plc_ip}")
        # Collect tag values from the PLC
        collect_tag_values(plc_ip)
    else:
        print("Failed to discover the PLC's IP address.")

if __name__ == "__main__":
    main()