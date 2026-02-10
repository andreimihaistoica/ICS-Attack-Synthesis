import socket
import pycomm3
from pycomm3 import LogixDriver

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Assuming the PLC is on the same subnet as the engineering workstation
    # This is a simple example using a broadcast to find the PLC
    broadcast_ip = '255.255.255.255'
    port = 44818  # Common port for EtherNet/IP

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(('', 0))

    # Send a broadcast message to discover the PLC
    sock.sendto(b'Who is PLC?', (broadcast_ip, port))

    # Receive the response
    data, addr = sock.recvfrom(1024)
    sock.close()

    if data:
        return addr[0]
    else:
        return None

# Function to perform an online edit to the PLC
def perform_online_edit(plc_ip):
    try:
        with LogixDriver(plc_ip) as plc:
            # Check if the PLC is in the correct mode (e.g., Run mode)
            if plc.get_plc_state() == 'RUN':
                print(f"PLC at {plc_ip} is in RUN mode. Proceeding with online edit.")
                
                # Example of modifying a tag (controller tasking or program)
                tag_name = 'ExampleTag'
                new_value = 12345  # Example value to set
                plc.write((tag_name, new_value))
                print(f"Modified tag {tag_name} to {new_value} successfully.")
            else:
                print(f"PLC at {plc_ip} is not in RUN mode. Cannot perform online edit.")
    except Exception as e:
        print(f"Error performing online edit: {e}")

# Main function
def main():
    plc_ip = discover_plc_ip()
    if plc_ip:
        print(f"Discovered PLC at IP address: {plc_ip}")
        perform_online_edit(plc_ip)
    else:
        print("Failed to discover PLC IP address.")

if __name__ == "__main__":
    main()