from scapy.all import ARP, Ether, srp
from pymodbus.client import ModbusTcpClient
import time

# Function to find the PLC's IP address
def find_plc_ip(network="192.168.1.0/24"):
    print("[*] Scanning network to find PLC IP...")
    
    # Create an ARP request packet
    arp = ARP(pdst=network)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    # Send the packet and capture responses
    result = srp(packet, timeout=3, verbose=False)[0]
    devices = {recv.psrc: recv.hwsrc for sent, recv in result}

    # Assuming a Schneider PLC has a known MAC prefix (modify if necessary)
    for ip, mac in devices.items():
        if mac.startswith("00:80:F4"):  # Schneider Electric OUI prefix
            print(f"[+] Found Schneider Electric PLC at IP: {ip}")
            return ip
    
    print("[-] No Schneider Electric PLC found on the network.")
    return None

# Function to collect information from the PLC via Modbus
def collect_plc_data(plc_ip):
    print("[*] Connecting to PLC at IP:", plc_ip)
    
    client = ModbusTcpClient(plc_ip, port=502)  # Default Modbus TCP port
    if not client.connect():
        print("[-] Failed to connect to PLC.")
        return

    print("[+] Connected to PLC. Collecting data...")

    # Read Holding Registers (Modify based on actual PLC register map)
    reg_start = 0  # Start of registers
    reg_count = 10  # Number of registers to read
    response = client.read_holding_registers(reg_start, reg_count, unit=1)
    
    if not response.isError():
        print(f"[+] Holding Registers Data: {response.registers}")
    else:
        print("[-] Failed to read holding registers.")

    # Read Device Information (Modbus Function Code 43/14 for Schneider Electric PLCs)
    response = client.read_device_information(unit=1)
    if not response.isError():
        print(f"[+] Device Information: {response.information}")
    else:
        print("[-] Failed to retrieve device information.")

    client.close()
    print("[+] Done.")

# Main execution
if __name__ == "__main__":
    plc_ip = find_plc_ip()  # Discover PLC IP
    if plc_ip:
        collect_plc_data(plc_ip)  # Collect data if PLC is found