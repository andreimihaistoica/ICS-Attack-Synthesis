import socket
import subprocess
import time

# Function to find the IP address of the PLC
def find_plc_ip():
    # Assuming the PLC is on the same network and responds to ping
    # This is a simple method to find the IP address of the PLC
    # You can replace this with a more sophisticated method if needed
    network = "10.0.0.0/24"  # Replace with your network range
    command = f"arp-scan -I eth0 -l {network}"  # Replace eth0 with your network interface
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    for line in result.stdout.splitlines():
        if "Micro850" in line:  # Assuming the PLC has a specific identifier in the ARP scan
            ip_address = line.split()[0]
            return ip_address
    return None

# Function to block a specific port on the serial to Ethernet converter
def block_port(ip_address, port):
    try:
        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the serial to Ethernet converter
        sock.connect((ip_address, port))
        print(f"Connected to {ip_address} on port {port}. Port is now blocked.")
        # Hold the connection open to block the port
        while True:
            time.sleep(1)
    except Exception as e:
        print(f"Failed to block port {port} on {ip_address}: {e}")

# Main function
def main():
    # Find the IP address of the PLC
    plc_ip = find_plc_ip()
    if plc_ip is None:
        print("Failed to find the PLC IP address.")
        return

    # IP address of the serial to Ethernet converter
    converter_ip = "10.0.0.1"  # Replace with the actual IP address of the converter

    # Port to block (e.g., 20001 for serial COM 1)
    port_to_block = 20001

    # Block the specified port
    block_port(converter_ip, port_to_block)

if __name__ == "__main__":
    main()