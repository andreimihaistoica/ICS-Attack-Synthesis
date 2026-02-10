import socket
import subprocess
import time

# Function to find the IP address of the Siemens S7-1200 PLC
def find_plc_ip():
    # Assuming the PLC is on the same network and responds to ping
    # This is a simple method and may need to be adjusted based on your network setup
    network = "10.0.0.0/24"  # Adjust this to your network range
    try:
        result = subprocess.run(['arp', '-a'], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if "S7-1200" in line:  # Adjust this to match the PLC's name or MAC address
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
        print(f"Connected to {ip} on port {port}. Blocking COM port...")
        # Hold the connection open indefinitely
        while True:
            time.sleep(1)
    except Exception as e:
        print(f"Error blocking COM port: {e}")

# Main function
def main():
    # Find the PLC's IP address
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"PLC IP address found: {plc_ip}")
        # Block the serial COM port (e.g., COM1 on port 20001)
        block_com_port(plc_ip, 20001)
    else:
        print("PLC IP address not found. Exiting.")

if __name__ == "__main__":
    main()