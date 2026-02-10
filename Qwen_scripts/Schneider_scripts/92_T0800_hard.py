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
    message = b'PLC_DISCOVERY'
    sock.sendto(message, (broadcast, 502))

    # Receive the response
    sock.settimeout(5)
    try:
        data, addr = sock.recvfrom(1024)
        if data == b'PLC_RESPONSE':
            return addr[0]
    except socket.timeout:
        print("No response from the PLC. Check the network configuration.")
    finally:
        sock.close()
    return None

# Function to activate firmware update mode
def activate_firmware_update_mode(ip_address):
    client = ModbusTcpClient(ip_address)
    try:
        client.connect()
        if client.is_socket_open():
            print(f"Connected to PLC at {ip_address}")

            # Write to a specific register to activate firmware update mode
            # Assuming the register address for firmware update mode is 0x0001
            result = client.write_coil(1, True)
            if result.isError():
                print("Failed to activate firmware update mode.")
            else:
                print("Firmware update mode activated successfully.")
        else:
            print("Failed to connect to the PLC.")
    except ConnectionException as e:
        print(f"Connection error: {e}")
    finally:
        client.close()

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        print(f"PLC found at IP address: {plc_ip}")
        # Activate firmware update mode
        activate_firmware_update_mode(plc_ip)
    else:
        print("PLC not found. Check the network configuration.")

if __name__ == "__main__":
    main()