import socket
import pymodbus
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# Default credentials for the Schneider Electric TM221CE16R PLC
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin"

# Function to find the PLC's IP address on the network
def find_plc_ip():
    # This is a simplified method to find the PLC's IP address.
    # In a real-world scenario, you might use network scanning tools like nmap.
    network = "192.168.1.0/24"  # Replace with your network range
    print("Scanning network for PLC...")
    for ip in [f"192.168.1.{i}" for i in range(1, 255)]:
        try:
            # Attempt to connect to the Modbus TCP port (502)
            client = ModbusTcpClient(ip, port=502)
            client.connect()
            if client.is_socket_open():
                print(f"PLC found at IP: {ip}")
                return ip
        except ConnectionException:
            continue
        finally:
            client.close()
    print("PLC not found on the network.")
    return None

# Function to attempt login with default credentials
def attempt_login(ip, username, password):
    try:
        client = ModbusTcpClient(ip, port=502)
        client.connect()
        if client.is_socket_open():
            print(f"Successfully connected to PLC at IP: {ip}")
            # Here you would implement the logic to use the default credentials
            # For demonstration, we'll just print a message
            print(f"Using default credentials: {username}/{password}")
            # Example: Read a register to verify access
            response = client.read_holding_registers(0, 1, unit=1)
            if response.isError():
                print("Failed to read register, check credentials.")
            else:
                print(f"Register value: {response.registers[0]}")
        else:
            print(f"Failed to connect to PLC at IP: {ip}")
    except ConnectionException as e:
        print(f"Connection error: {e}")
    finally:
        client.close()

# Main function
def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        attempt_login(plc_ip, DEFAULT_USERNAME, DEFAULT_PASSWORD)

if __name__ == "__main__":
    main()