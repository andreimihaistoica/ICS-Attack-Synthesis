import socket
from pymodbus.client.sync import ModbusTcpClient
from scapy.all import ARP, Ether, srp
import struct

def discover_plc_ip(network):
    """
    Discover the IP address of the PLC on the network. 
    This will perform an ARP scan on the given network range.
    """
    print("[*] Scanning network for PLC devices...")
    arp_request = ARP(pdst=network)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = srp(arp_request_broadcast, timeout=3, verbose=0)[0]
    
    for element in answered_list:
        print(f"[+] Found device: IP={element[1].psrc}, MAC={element[1].hwsrc}")
        # Implement a way to distinguish the PLC if needed, for now returning the first detected IP
        return element[1].psrc
    
    print("[-] No devices found on the network.")
    return None

def fetch_plc_tags(plc_ip):
    """
    Connect to the PLC and retrieve point/tag information.
    This part assumes the PLC is using Modbus TCP and tags/pointers
    are stored within specific register ranges.
    """
    try:
        print(f"[*] Connecting to PLC at IP {plc_ip}...")
        client = ModbusTcpClient(plc_ip)

        if not client.connect():
            print("[-] Could not connect to the PLC.")
            return

        print("[*] Connected to PLC. Fetching tag information...")

        # Read holding registers (for example) to fetch process-related points
        start_register = 0  # Assuming this is where tags or process data begins
        num_registers = 10  # Number of registers to read (adjust as needed)
        response = client.read_holding_registers(start_register, num_registers)

        if not response.isError():
            print("[+] Retrieved data from PLC:")
            for i, value in enumerate(response.registers):
                print(f"    Register {start_register + i}: {value}")
        else:
            print(f"[-] Error reading registers: {response}")
        
        client.close()

    except Exception as e:
        print(f"[-] An error occurred: {e}")

def main():
    # Replace '192.168.1.0/24' with the network range to scan
    network_range = '192.168.1.0/24'

    # Step 1: Discover the PLC's IP address
    plc_ip = discover_plc_ip(network_range)
    
    if plc_ip:
        print(f"[+] PLC IP Address found: {plc_ip}")
        
        # Step 2: Fetch point and tag information
        fetch_plc_tags(plc_ip)
    else:
        print("[-] Could not find a PLC on the network. Exiting.")


if __name__ == "__main__":
    main()