from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException
import socket
import sys

def find_plc_ip(network_prefix, start_range, end_range, port=502):
    """
    Scans the network to find the PLC's IP address.
    :param network_prefix: The first three octets of the IP address (e.g., '192.168.1').
    :param start_range: The starting range for the last octet.
    :param end_range: The ending range for the last octet.
    :param port: The Modbus TCP port (default is 502).
    :return: The IP address of the PLC if found, otherwise None.
    """
    for i in range(start_range, end_range + 1):
        ip_address = f"{network_prefix}.{i}"
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.5)
                result = sock.connect_ex((ip_address, port))
                if result == 0:
                    print(f"PLC found at IP: {ip_address}")
                    return ip_address
        except Exception as e:
            print(f"Error checking {ip_address}: {e}")
    print("PLC not found in the specified range.")
    return None

def restart_plc(ip_address):
    """
    Sends a command to restart the PLC.
    :param ip_address: The IP address of the PLC.
    """
    try:
        client = ModbusTcpClient(ip_address)
        client.connect()
        
        # Example Modbus command to restart the PLC
        # Note: The actual function code and address may vary based on the PLC model and configuration
        # This is a placeholder and should be replaced with the correct Modbus command
        response = client.write_coil(address=0, value=True)
        
        if response.isError():
            print(f"Failed to send restart command: {response}")
        else:
            print("Restart command sent successfully.")
            
        client.close()
    except ModbusException as e:
        print(f"Modbus error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Define the network prefix and IP range to scan
    network_prefix = "192.168.1"  # Adjust this to match your network
    start_range = 100
    end_range = 150
    
    # Find the PLC's IP address
    plc_ip = find_plc_ip(network_prefix, start_range, end_range)
    
    if plc_ip:
        # Restart the PLC
        restart_plc(plc_ip)
    else:
        print("PLC IP address not found. Exiting.")
        sys.exit(1)