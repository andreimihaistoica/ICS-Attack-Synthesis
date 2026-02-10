import os
import re
from scapy.all import ARP, Ether, srp
from pymodbus.client import ModbusTcpClient

def find_plc_ip():
    # Define the IP range to scan (e.g., 192.168.1.0/24)
    ip_range = "192.168.1.0/24"
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and receive the response
    result = srp(packet, timeout=2, verbose=0)[0]

    # Parse the response to find the PLC's IP
    plc_ip = None
    for sent, received in result:
        # Assuming the PLC has a specific MAC address prefix (e.g., 00:1D:9C)
        if received.hwsrc.startswith("00:1D:9C"):
            plc_ip = received.psrc
            print(f"PLC found at IP: {plc_ip}")
            break

    if plc_ip is None:
        print("PLC not found on the network.")
        exit(1)

    return plc_ip

def activate_firmware_update_mode(plc_ip):
    # Connect to the PLC using Modbus TCP
    client = ModbusTcpClient(plc_ip)
    if not client.connect():
        print(f"Failed to connect to PLC at {plc_ip}")
        exit(1)

    # Define the Modbus command to activate firmware update mode
    # This is a hypothetical register/function code; adjust based on the PLC's documentation
    register_address = 0x1000  # Example register address for firmware mode
    value_to_write = 1         # Example value to activate firmware update mode

    # Write the value to the register
    try:
        response = client.write_register(register_address, value_to_write)
        if response.isError():
            print(f"Failed to activate firmware update mode: {response}")
        else:
            print("Firmware update mode activated successfully.")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()

    # Step 2: Activate firmware update mode
    activate_firmware_update_mode(plc_ip)