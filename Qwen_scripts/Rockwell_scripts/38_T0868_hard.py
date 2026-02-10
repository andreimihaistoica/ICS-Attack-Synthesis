import pycomm3
import socket
import time

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Use a broadcast to find the PLC
    broadcast_ip = '255.255.255.255'
    port = 44818  # Ethernet/IP port

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Send a broadcast message
    message = b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    sock.sendto(message, (broadcast_ip, port))

    # Receive the response
    sock.settimeout(5)
    try:
        data, addr = sock.recvfrom(1024)
        return addr[0]
    except socket.timeout:
        print("No PLC found")
        return None

# Function to read the operating mode of the PLC
def read_operating_mode(plc_ip):
    try:
        # Create a PLC object
        plc = pycomm3.LogixDriver(plc_ip)

        # Open the connection
        plc.open()

        # Read the operating mode
        operating_mode = plc.get_plc_status()['state']

        # Close the connection
        plc.close()

        return operating_mode
    except Exception as e:
        print(f"Error reading operating mode: {e}")
        return None

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip is None:
        print("Failed to discover PLC IP address")
        return

    print(f"PLC IP address: {plc_ip}")

    # Read the operating mode
    operating_mode = read_operating_mode(plc_ip)
    if operating_mode is not None:
        print(f"PLC Operating Mode: {operating_mode}")
    else:
        print("Failed to read operating mode")

if __name__ == "__main__":
    main()