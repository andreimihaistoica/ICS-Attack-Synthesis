from scapy.all import ARP, Ether, srp
from pymodbus.client import ModbusTcpClient

# Network range to scan (Modify based on your network)
NETWORK_RANGE = "192.168.1.1/24"

def find_plc_ip():
    """
    Scan the local network to identify the PLC IP address.
    Assumes the PLC responds to ARP requests.
    """
    print("[*] Scanning network for PLC device...")
    arp_request = ARP(pdst=NETWORK_RANGE)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")  # Broadcast request
    packet = ether / arp_request
    result = srp(packet, timeout=2, verbose=False)[0]

    for sent, received in result:
        print(f"[+] Possible device found: {received.psrc}")
        # Add logic to filter PLC-specific MAC addresses or IP ranges if needed.
        return received.psrc  # Returning the first detected device (modify as needed)
    
    print("[-] No PLC detected.")
    return None

def collect_io_image(plc_ip):
    """
    Connect to the PLC using ModbusTCP and gather I/O Image data.
    Adjust register addresses based on your PLC model.
    """
    if not plc_ip:
        print("[-] No IP address found for the PLC. Exiting.")
        return

    print(f"[*] Connecting to PLC at {plc_ip}...")
    client = ModbusTcpClient(plc_ip)

    if not client.connect():
        print(f"[-] Failed to connect to PLC at {plc_ip}. Check network or PLC settings.")
        return
    
    print("[+] Connected to PLC. Reading I/O Image...")

    # Example addresses (Modify based on PLC config):
    input_register_address = 0  # Modify based on PLC address map
    output_register_address = 100  # Modify based on PLC address map
    register_count = 10  # Number of registers to read (Tweak as per system)

    # Reading Input Image Table
    inputs = client.read_discrete_inputs(input_register_address, register_count)
    if inputs.isError():
        print("[-] Error reading input image table.")
    else:
        print(f"[+] Input Image: {inputs.bits}")

    # Reading Output Image Table
    outputs = client.read_coils(output_register_address, register_count)
    if outputs.isError():
        print("[-] Error reading output image table.")
    else:
        print(f"[+] Output Image: {outputs.bits}")

    client.close()

# Execute the script
if __name__ == "__main__":
    plc_ip = find_plc_ip()
    collect_io_image(plc_ip)