import socket
import struct
import time
from pycomm3 import LogixDriver, PLC

# Default credentials for Siemens S7-1200 PLC
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin"

# Function to discover the IP address of the PLC
def discover_plc_ip():
    # Define the broadcast address and port
    broadcast_address = '255.255.255.255'
    port = 102

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Send a broadcast message to discover the PLC
    discovery_message = b'\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    sock.sendto(discovery_message, (broadcast_address, port))

    # Set a timeout for receiving the response
    sock.settimeout(5)

    try:
        # Receive the response
        data, addr = sock.recvfrom(1024)
        plc_ip = addr[0]
        print(f"PLC found at IP address: {plc_ip}")
        return plc_ip
    except socket.timeout:
        print("No PLC found. Please check the network configuration.")
        return None
    finally:
        sock.close()

# Function to connect to the PLC using default credentials
def connect_to_plc(plc_ip):
    try:
        # Create a PLC driver
        plc = PLC()
        plc.open(plc_ip)

        # Log in using default credentials
        if plc.login(DEFAULT_USERNAME, DEFAULT_PASSWORD):
            print("Successfully connected to the PLC using default credentials.")
            return plc
        else:
            print("Failed to connect to the PLC using default credentials.")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Function to perform actions on the PLC
def perform_actions(plc):
    try:
        # Example action: Read the Motor_Temp tag
        motor_temp = plc.read('Motor_Temp')
        print(f"Motor Temperature: {motor_temp}")

        # Example action: Set a tag (e.g., Activate_Fan_A)
        plc.write('Activate_Fan_A', True)
        print("Activated Fan A")

        # Add more actions as needed
    except Exception as e:
        print(f"An error occurred while performing actions: {e}")

# Main function
def main():
    # Discover the PLC IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        # Connect to the PLC using default credentials
        plc = connect_to_plc(plc_ip)
        if plc:
            # Perform actions on the PLC
            perform_actions(plc)
            # Close the connection
            plc.close()

if __name__ == "__main__":
    main()