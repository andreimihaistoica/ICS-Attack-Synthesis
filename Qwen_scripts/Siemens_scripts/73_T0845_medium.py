import snap7
import socket
import struct
import os

# Function to discover the IP address of the Siemens S7-1200 PLC
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

    # Receive the response
    sock.settimeout(5)
    try:
        data, addr = sock.recvfrom(1024)
        ip_address = addr[0]
        print(f"Discovered PLC at IP address: {ip_address}")
        return ip_address
    except socket.timeout:
        print("No PLC found. Please ensure the PLC is connected and the network is configured correctly.")
        return None

# Function to upload the program from the PLC
def upload_program_from_plc(ip_address):
    if not ip_address:
        print("No valid IP address provided.")
        return

    # Create a client object
    client = snap7.client.Client()

    # Connect to the PLC
    try:
        client.connect(ip_address, 0, 1)
        print(f"Connected to PLC at {ip_address}")
    except Exception as e:
        print(f"Failed to connect to PLC: {e}")
        return

    # Read the program from the PLC
    try:
        # Assuming the program is stored in a block (e.g., DB1)
        block_type = snap7.types.AG_DATA_BLOCK
        block_num = 1
        block_size = 1024  # Adjust the size as needed

        data = client.db_read(block_num, 0, block_size)
        print(f"Program data read from PLC: {data}")

        # Save the program data to a file
        with open('plc_program.bin', 'wb') as file:
            file.write(data)
        print("Program data saved to plc_program.bin")
    except Exception as e:
        print(f"Failed to read program from PLC: {e}")
    finally:
        client.disconnect()
        print("Disconnected from PLC")

# Main function
def main():
    # Discover the PLC IP address
    plc_ip = discover_plc_ip()

    # Upload the program from the PLC
    upload_program_from_plc(plc_ip)

if __name__ == "__main__":
    main()