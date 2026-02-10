import socket
import struct
import time
import requests

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the broadcast address and port
    broadcast_address = '192.168.9.255'
    port = 502  # Modbus TCP port

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Send a broadcast message to discover the PLC
    discovery_message = b'\x00\x01\x00\x00\x00\x06\x01\x03\x00\x00\x00\x01'
    sock.sendto(discovery_message, (broadcast_address, port))

    # Receive the response
    sock.settimeout(5)
    try:
        data, addr = sock.recvfrom(1024)
        plc_ip = addr[0]
        print(f"PLC IP Address discovered: {plc_ip}")
        return plc_ip
    except socket.timeout:
        print("No response from the PLC. Check the network configuration.")
        return None

# Function to send a restart/shutdown command to the PLC
def send_restart_command(plc_ip):
    # Define the Modbus TCP request for a device restart
    # This is a simplified example. The actual command may vary based on the PLC's firmware and configuration.
    restart_command = b'\x00\x01\x00\x00\x00\x06\x01\x06\x00\x00\x00\x01'

    # Create a TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)

    try:
        # Connect to the PLC
        sock.connect((plc_ip, 502))
        print(f"Connected to PLC at {plc_ip}")

        # Send the restart command
        sock.send(restart_command)
        print("Restart command sent to the PLC")

        # Receive the response
        response = sock.recv(1024)
        print(f"Response from PLC: {response}")

    except socket.error as e:
        print(f"Error: {e}")
    finally:
        sock.close()

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        # Send the restart command
        send_restart_command(plc_ip)

if __name__ == "__main__":
    main()