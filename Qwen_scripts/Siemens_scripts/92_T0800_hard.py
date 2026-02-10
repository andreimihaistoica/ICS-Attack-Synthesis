import socket
import netifaces as ni
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException

# Function to find the PLC's IP address
def find_plc_ip():
    # Get all network interfaces
    interfaces = ni.interfaces()
    for interface in interfaces:
        try:
            # Get the IP address of the interface
            ip = ni.ifaddresses(interface)[ni.AF_INET][0]['addr']
            # Check if the IP is in the local network
            if ip.startswith('192.168'):
                # Try to connect to the PLC
                client = ModbusTcpClient(ip, port=502)
                if client.connect():
                    print(f"PLC found at IP: {ip}")
                    client.close()
                    return ip
        except (KeyError, ConnectionException):
            continue
    return None

# Function to activate firmware update mode
def activate_firmware_update_mode(plc_ip):
    client = ModbusTcpClient(plc_ip, port=502)
    try:
        if client.connect():
            # Write to a specific register to activate firmware update mode
            # This is a hypothetical register; you need to know the actual register address
            result = client.write_register(0x0001, 1)
            if result.isError():
                print("Failed to activate firmware update mode")
            else:
                print("Firmware update mode activated successfully")
        else:
            print("Failed to connect to the PLC")
    finally:
        client.close()

# Main function
def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        activate_firmware_update_mode(plc_ip)
    else:
        print("PLC not found in the network")

if __name__ == "__main__":
    main()