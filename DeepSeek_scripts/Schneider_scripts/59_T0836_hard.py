from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from pymodbus.constants import Endian
import socket
import struct

def find_plc_ip(subnet):
    """
    Scans the network to find the PLC's IP address.
    :param subnet: The subnet to scan (e.g., '192.168.9.')
    :return: The PLC's IP address or None if not found.
    """
    for i in range(1, 255):
        ip = subnet + str(i)
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(0.1)
                result = sock.connect_ex((ip, 502))  # Modbus TCP port
                if result == 0:
                    print(f"Found PLC at IP: {ip}")
                    return ip
        except Exception as e:
            continue
    print("PLC not found on the network.")
    return None

def modify_timer_preset(ip, timer_address, new_preset):
    """
    Modifies the timer preset value in the PLC.
    :param ip: The PLC's IP address.
    :param timer_address: The address of the timer to modify.
    :param new_preset: The new preset value to set.
    """
    try:
        # Connect to the PLC
        client = ModbusTcpClient(ip)
        if not client.connect():
            print("Failed to connect to the PLC.")
            return

        # Write the new preset value to the timer
        builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)
        builder.add_32bit_uint(new_preset)  # Assuming the timer preset is a 32-bit unsigned integer
        payload = builder.to_registers()

        client.write_registers(timer_address, payload, unit=1)
        print(f"Modified timer preset at address {timer_address} to {new_preset} seconds.")

    except Exception as e:
        print(f"Error modifying timer preset: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    # Define the subnet to scan for the PLC
    subnet = "192.168.9."

    # Find the PLC's IP address
    plc_ip = find_plc_ip(subnet)
    if not plc_ip:
        exit(1)

    # Modify the timer preset value (e.g., change Timer0's preset to 30 seconds)
    timer_address = 0  # Address of Timer0 (adjust as needed)
    new_preset = 30  # New preset value in seconds
    modify_timer_preset(plc_ip, timer_address, new_preset)