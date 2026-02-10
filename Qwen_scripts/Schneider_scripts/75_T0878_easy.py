import socket
import netifaces as ni
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# Function to discover the PLC's IP address
def discover_plc_ip():
    # List all network interfaces
    interfaces = ni.interfaces()
    for interface in interfaces:
        try:
            # Get the IP address of the interface
            ip = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
            # Check if the IP is in the local network (e.g., 192.168.x.x)
            if ip.startswith('192.168'):
                # Try to connect to the PLC
                client = ModbusTcpClient(ip)
                if client.connect():
                    print(f"PLC found at IP: {ip}")
                    client.close()
                    return ip
        except (KeyError, ConnectionException):
            continue
    print("PLC not found in the local network.")
    return None

# Function to suppress alarms
def suppress_alarms(plc_ip):
    client = ModbusTcpClient(plc_ip)
    try:
        if client.connect():
            print("Connected to PLC.")
            
            # Example: Suppress an alarm by setting a specific register to 0
            # This is a hypothetical example; the actual register and value will depend on the PLC and its configuration
            register_address = 0x0001  # Example register address
            value_to_write = 0  # Example value to suppress the alarm
            
            # Write the value to the register
            result = client.write_register(register_address, value_to_write)
            if result.isError():
                print("Failed to suppress alarm.")
            else:
                print("Alarm suppressed successfully.")
        else:
            print("Failed to connect to PLC.")
    except ConnectionException as e:
        print(f"Connection error: {e}")
    finally:
        client.close()

# Main function
def main():
    plc_ip = discover_plc_ip()
    if plc_ip:
        suppress_alarms(plc_ip)

if __name__ == "__main__":
    main()