import socket
import netifaces as ni
from pyModbusTCP.client import ModbusClient
import time

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Get all network interfaces
    interfaces = ni.interfaces()
    for interface in interfaces:
        try:
            # Get the IP address of the interface
            ip = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
            if ip != '127.0.0.1':  # Exclude loopback address
                # Try to connect to the PLC
                client = ModbusClient(host=ip, port=502, auto_open=True, auto_close=True)
                if client.is_open():
                    print(f"PLC found at IP: {ip}")
                    return ip
        except Exception as e:
            print(f"Error checking interface {interface}: {e}")
    print("PLC not found on any network interface.")
    return None

# Function to manipulate the I/O image
def manipulate_io_image(plc_ip, input_address, output_address, input_value, output_value):
    client = ModbusClient(host=plc_ip, port=502, auto_open=True, auto_close=True)
    
    if not client.is_open():
        print("Failed to connect to the PLC.")
        return
    
    # Override the status of a physical discrete input
    client.write_single_coil(input_address, input_value)
    print(f"Input at address {input_address} set to {input_value}")
    
    # Override the status of a physical discrete output
    client.write_single_coil(output_address, output_value)
    print(f"Output at address {output_address} set to {output_value}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip is None:
        return
    
    # Define the I/O addresses and values to manipulate
    input_address = 0  # Example input address
    output_address = 1  # Example output address
    input_value = True  # Example input value (True or False)
    output_value = False  # Example output value (True or False)
    
    # Manipulate the I/O image
    manipulate_io_image(plc_ip, input_address, output_address, input_value, output_value)

if __name__ == "__main__":
    main()