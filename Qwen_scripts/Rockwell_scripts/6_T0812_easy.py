import subprocess
import pymodbus.client.sync as modbus
from pymodbus.exceptions import ConnectionException

# Default credentials for the PLC
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin123"

# Function to discover the PLC's IP address
def discover_plc_ip():
    print("Discovering PLC IP address...")
    # Run nmap to scan the network for devices
    nmap_output = subprocess.check_output(["nmap", "-sn", "192.168.1.0/24"]).decode("utf-8")
    devices = nmap_output.split("\n")
    
    # Filter out the IP addresses
    ip_addresses = [line.split()[4] for line in devices if "Nmap scan report for" in line]
    
    # Assume the PLC is the first device found (for simplicity)
    if ip_addresses:
        return ip_addresses[0]
    else:
        raise Exception("No devices found on the network")

# Function to connect to the PLC using default credentials
def connect_to_plc(ip_address):
    print(f"Connecting to PLC at {ip_address}...")
    client = modbus.ModbusTcpClient(ip_address)
    
    try:
        if client.connect():
            print("Connection successful")
            return client
        else:
            raise ConnectionException("Failed to connect to the PLC")
    except ConnectionException as e:
        print(f"Connection error: {e}")
        return None

# Function to perform actions on the PLC
def perform_actions(client):
    print("Performing actions on the PLC...")
    # Example: Read a register
    try:
        response = client.read_holding_registers(0, 1, unit=1)
        if response.isError():
            print("Error reading register")
        else:
            print(f"Register value: {response.registers[0]}")
    except Exception as e:
        print(f"Error performing actions: {e}")

# Main function
def main():
    try:
        # Discover the PLC's IP address
        plc_ip = discover_plc_ip()
        
        # Connect to the PLC using default credentials
        client = connect_to_plc(plc_ip)
        
        if client:
            # Perform actions on the PLC
            perform_actions(client)
            
            # Close the connection
            client.close()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()