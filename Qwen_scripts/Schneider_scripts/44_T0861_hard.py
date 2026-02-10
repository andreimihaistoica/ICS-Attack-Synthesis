import socket
import pymodbus
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# Function to discover the PLC's IP address
def discover_plc_ip(subnet='192.168.9.0', netmask='255.255.255.0'):
    network = subnet.split('.')
    network[-1] = '0'
    network = '.'.join(network)
    broadcast = subnet.split('.')
    broadcast[-1] = '255'
    broadcast = '.'.join(broadcast)

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind((network, 0))

    # Send a broadcast message to discover the PLC
    message = b'Who is the PLC?'
    sock.sendto(message, (broadcast, 502))

    # Receive the response
    sock.settimeout(5)
    try:
        data, addr = sock.recvfrom(1024)
        print(f"PLC found at IP address: {addr[0]}")
        return addr[0]
    except socket.timeout:
        print("No PLC found on the network.")
        return None

# Function to read tags from the PLC
def read_tags(plc_ip):
    client = ModbusTcpClient(plc_ip)

    try:
        client.connect()

        # Define the tags and their addresses
        tags = {
            'M_ACTFAN': 1,
            'M_TOG': 2,
            'Q_FAN': 0,
            'Q_REDA': 4,
            'Q_GREENA': 5,
            'SB_TB1S': 6,
            'Counter0': 0,
            'Timer0': 0,
            'Timer1': 1
        }

        # Read the tags
        for tag, address in tags.items():
            if tag in ['M_ACTFAN', 'M_TOG', 'Q_FAN', 'Q_REDA', 'Q_GREENA', 'SB_TB1S']:
                result = client.read_coils(address, 1)
                value = result.bits[0]
            elif tag in ['Counter0']:
                result = client.read_holding_registers(address, 1)
                value = result.registers[0]
            elif tag in ['Timer0', 'Timer1']:
                result = client.read_input_registers(address, 2)
                value = (result.registers[0] << 16) + result.registers[1]

            print(f"{tag}: {value}")

    except ConnectionException:
        print("Failed to connect to the PLC.")
    finally:
        client.close()

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()

    if plc_ip:
        # Read the tags from the PLC
        read_tags(plc_ip)

if __name__ == "__main__":
    main()