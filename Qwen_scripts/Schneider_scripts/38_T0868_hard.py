import socket
import netifaces as ni
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Get all network interfaces
    interfaces = ni.interfaces()
    
    for interface in interfaces:
        # Get the IP address of the interface
        try:
            ip = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
            if ip != '127.0.0.1':  # Exclude loopback
                # Try to connect to the PLC
                client = ModbusTcpClient(ip, port=502)
                if client.connect():
                    print(f"PLC found at IP: {ip}")
                    client.close()
                    return ip
        except (KeyError, ConnectionException):
            continue
    
    print("PLC not found on the network.")
    return None

# Function to read the operating mode of the PLC
def read_operating_mode(ip):
    client = ModbusTcpClient(ip, port=502)
    
    try:
        if client.connect():
            # Read the operating mode from a specific register (example: register 0)
            result = client.read_holding_registers(0, 1, unit=1)
            if result.isError():
                print("Error reading operating mode.")
            else:
                mode = result.registers[0]
                print(f"Operating Mode: {mode}")
        else:
            print("Failed to connect to the PLC.")
    finally:
        client.close()

# Main function
def main():
    plc_ip = discover_plc_ip()
    if plc_ip:
        read_operating_mode(plc_ip)

if __name__ == "__main__":
    main()