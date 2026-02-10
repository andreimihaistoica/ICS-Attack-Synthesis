import socket
import time
import os
import subprocess

# Configuration
SERIAL_CONVERTER_IP = "10.0.0.1"  # Replace with the actual IP address
COM_PORT_BASE = 20000 # Base Port number for the Serial to Ethernet converter
COM_PORTS_TO_BLOCK = [1, 2, 3] # Serial COM ports to block

def get_plc_ip_address():
    """
    Placeholder function to get the PLC's IP address.
    Replace this with actual code that retrieves the PLC's IP.
    This might involve reading from a configuration file,
    querying a network service, or using a discovery protocol.
    """
    # Implement method to find PLC IP Address
    # Example:
    #   - Read from a config file
    #   - Scan network for device
    #   - Use a known IP (less robust)
    
    print("Attempting to determine PLC IP Address...")
    
    # Simulate the process of finding the IP.  Replace with actual code.
    # In a real scenario, you might query the network, read from a 
    # configuration file, or use a known IP if discovery is not possible.
    
    # Replace with your actual method to find the PLC IP
    plc_ip = "192.168.1.10"  # Placeholder IP
    
    print(f"PLC IP Address determined to be: {plc_ip}")
    return plc_ip
    
def block_serial_com_port(ip_address, port):
    """Blocks a serial COM port by opening and holding a TCP connection."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip_address, port))
        print(f"Successfully blocked serial COM port {port} on {ip_address}")

        # Keep the connection open indefinitely
        while True:
            time.sleep(60)  # Sleep for 60 seconds to prevent CPU usage
            # Optionally, send a keep-alive signal to prevent the connection from closing:
            # s.send(b"keep-alive")
    except Exception as e:
        print(f"Error blocking serial COM port {port}: {e}")
    finally:
        #This is probably not necessary, since the script runs until stopped, and we want to keep the connection open
        #s.close()
        pass


def main():
    """Main function to block serial COM ports."""
    #Step 1: Get the PLC IP Address
    plc_ip = get_plc_ip_address()

    #Step 2: Block the Serial COM ports

    for com_port in COM_PORTS_TO_BLOCK:
        port_to_block = COM_PORT_BASE + com_port
        print(f"Attempting to block serial COM port: {com_port} (TCP port: {port_to_block})")
        block_serial_com_port(SERIAL_CONVERTER_IP, port_to_block)  # Use the converter's IP

if __name__ == "__main__":
    main()