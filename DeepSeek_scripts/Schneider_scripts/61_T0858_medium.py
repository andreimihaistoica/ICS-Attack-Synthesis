from scapy.all import ARP, Ether, srp
from pymodbus.client import ModbusTcpClient

def find_plc_ip():
    # Define the IP range to scan (adjust as needed)
    ip_range = "192.168.1.1/24"
    
    # Create an ARP request packet
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and receive the response
    result = srp(packet, timeout=2, verbose=0)[0]

    # Extract the IP addresses of devices that responded
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    # Assuming the PLC has a known MAC prefix (e.g., 00:80:41 for Schneider Electric)
    plc_mac_prefix = "00:80:41"
    for device in devices:
        if device['mac'].startswith(plc_mac_prefix):
            return device['ip']
    
    return None

def change_plc_mode(ip_address, mode):
    # Connect to the PLC using Modbus TCP
    client = ModbusTcpClient(ip_address)
    if not client.connect():
        print(f"Failed to connect to PLC at {ip_address}")
        return

    # Define the Modbus address for changing the operating mode
    # This address may vary depending on the PLC model and configuration
    mode_address = 0x1000  # Example address, adjust as needed

    # Write the desired mode to the PLC
    # Mode values: 0 = Stop, 1 = Run, 2 = Program, etc. (adjust based on PLC documentation)
    mode_value = mode
    client.write_register(mode_address, mode_value)

    # Verify the mode change
    response = client.read_holding_registers(mode_address, 1)
    if response.registers[0] == mode_value:
        print(f"Successfully changed PLC mode to {mode}")
    else:
        print(f"Failed to change PLC mode")

    client.close()

if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"Found PLC at IP: {plc_ip}")
        
        # Step 2: Change the PLC's operating mode (e.g., to Program mode)
        change_plc_mode(plc_ip, mode=2)  # Mode 2 = Program mode
    else:
        print("PLC not found on the network")