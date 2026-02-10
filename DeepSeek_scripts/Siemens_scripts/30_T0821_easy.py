import socket
import struct
from time import sleep

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Broadcast a message to discover the PLC
    broadcast_ip = "255.255.255.255"
    broadcast_port = 47808  # Commonly used port for PLC discovery
    message = b"PLC_DISCOVERY_REQUEST"

    # Create a UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(5)  # Set timeout for response

    # Send discovery message
    sock.sendto(message, (broadcast_ip, broadcast_port))

    try:
        # Receive response from PLC
        data, addr = sock.recvfrom(1024)
        plc_ip = addr[0]
        print(f"Discovered PLC at IP: {plc_ip}")
        return plc_ip
    except socket.timeout:
        print("PLC discovery timed out. PLC not found.")
        return None
    finally:
        sock.close()

# Function to modify the controller tasking
def modify_controller_tasking(plc_ip):
    # Simulate connecting to the PLC and modifying tasking
    print(f"Connecting to PLC at {plc_ip}...")
    sleep(2)  # Simulate connection delay

    # Simulate modifying tasking (e.g., adding a malicious program to OB1)
    print("Modifying tasking...")
    sleep(2)  # Simulate task modification delay

    # Example: Associate a malicious program with OB1
    malicious_program = "Malicious_Program"
    task = "OB1"
    print(f"Associated {malicious_program} with {task} for cyclic execution.")

# Main script execution
if __name__ == "__main__":
    # Step 1: Discover PLC's IP address
    plc_ip = discover_plc_ip()

    if plc_ip:
        # Step 2: Modify controller tasking
        modify_controller_tasking(plc_ip)
    else:
        print("PLC discovery failed. Exiting script.")