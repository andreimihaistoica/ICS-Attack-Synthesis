import socket
import pymodbus
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# Function to discover the PLC's IP address
def discover_plc_ip():
    # This is a simple example of discovering the PLC's IP address.
    # In a real-world scenario, you might use a network scanning tool or a predefined list of IPs.
    # For this example, we'll assume the PLC is on the same subnet and use a simple scan.
    for ip in range(1, 255):
        ip_address = f"192.168.1.{ip}"
        try:
            # Attempt to connect to the IP address
            with socket.create_connection((ip_address, 502), timeout=1) as sock:
                print(f"PLC found at {ip_address}")
                return ip_address
        except (socket.timeout, ConnectionRefusedError):
            continue
    print("PLC not found")
    return None

# Function to modify alarm settings
def modify_alarm_settings(plc_ip):
    try:
        # Connect to the PLC
        client = ModbusTcpClient(plc_ip)
        client.connect()

        # Example: Disable alarm for a specific condition
        # Assuming the alarm setting is stored in a specific register (e.g., register 100)
        register_address = 100
        new_value = 0  # 0 to disable the alarm, 1 to enable it

        # Write the new value to the register
        result = client.write_register(register_address, new_value)
        if result.isError():
            print("Failed to modify alarm settings")
        else:
            print("Alarm settings modified successfully")

        # Close the connection
        client.close()
    except ConnectionException as e:
        print(f"Connection error: {e}")

# Main function
def main():
    plc_ip = discover_plc_ip()
    if plc_ip:
        modify_alarm_settings(plc_ip)

if __name__ == "__main__":
    main()