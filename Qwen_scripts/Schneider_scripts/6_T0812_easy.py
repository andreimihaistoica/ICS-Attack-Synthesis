import netifaces as ni
import socket
import pymodbus.client.sync as modbus_client
from pymodbus.exceptions import ConnectionException

# Default credentials for the PLC
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin123"

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Get all network interfaces
    interfaces = ni.interfaces()
    
    for interface in interfaces:
        try:
            # Get the IP address of the interface
            ip = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
            if ip == '127.0.0.1':
                continue  # Skip loopback interface
            
            # Attempt to connect to the PLC using the IP address
            client = modbus_client.ModbusTcpClient(ip)
            if client.connect():
                print(f"PLC found at IP address: {ip}")
                client.close()
                return ip
        except (KeyError, ConnectionException):
            continue
    
    print("PLC not found on the network.")
    return None

# Function to log into the PLC using default credentials
def login_plc(ip, username, password):
    try:
        client = modbus_client.ModbusTcpClient(ip)
        if client.connect():
            print(f"Connected to PLC at IP address: {ip}")
            
            # Simulate login with default credentials
            # Note: This is a placeholder. Actual login logic would depend on the PLC's authentication mechanism.
            if username == DEFAULT_USERNAME and password == DEFAULT_PASSWORD:
                print("Login successful with default credentials.")
            else:
                print("Login failed.")
            
            client.close()
        else:
            print("Failed to connect to the PLC.")
    except ConnectionException as e:
        print(f"Connection error: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    
    if plc_ip:
        # Attempt to log into the PLC using default credentials
        login_plc(plc_ip, DEFAULT_USERNAME, DEFAULT_PASSWORD)

if __name__ == "__main__":
    main()