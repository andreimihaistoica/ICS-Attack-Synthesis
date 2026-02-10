import socket
import pycomm3
from pycomm3 import LogixDriver

def discover_plc_ip():
    # Define the broadcast address and port for the PLC
    broadcast_address = '255.255.255.255'
    port = 44818  # Common port for EtherNet/IP

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(5)  # Set a timeout for the socket

    # Send a broadcast message to discover the PLC
    message = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    sock.sendto(message, (broadcast_address, port))

    try:
        # Receive the response
        data, addr = sock.recvfrom(1024)
        print(f"PLC found at IP address: {addr[0]}")
        return addr[0]
    except socket.timeout:
        print("No PLC found on the network.")
        return None
    finally:
        sock.close()

def upload_plc_program(plc_ip):
    try:
        # Connect to the PLC
        with LogixDriver(plc_ip) as plc:
            # Upload the program
            program = plc.get_program()
            if program:
                print("Program uploaded successfully.")
                # Save the program to a file
                with open('plc_program.l5x', 'w') as file:
                    file.write(program)
                print("Program saved to plc_program.l5x")
            else:
                print("Failed to upload the program.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    plc_ip = discover_plc_ip()
    if plc_ip:
        upload_plc_program(plc_ip)