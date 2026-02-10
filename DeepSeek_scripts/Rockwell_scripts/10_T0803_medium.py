from scapy.all import *
import subprocess
import re

def find_plc_ip():
    # Run a ping scan to find the PLC in the local network
    arp_scan = subprocess.check_output(["arp", "-a"]).decode('utf-8')
    
    # Assume the PLC's MAC address is known or has a specific prefix (e.g., Rockwell's OUI)
    plc_mac_pattern = re.compile(r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})")
    plc_ip = None
    
    for line in arp_scan.splitlines():
        if "Micro850" in line:  # Adjust this if the PLC's name is known
            ip_match = re.search(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", line)
            if ip_match:
                plc_ip = ip_match.group(0)
                break
    
    if not plc_ip:
        raise Exception("PLC IP address not found. Ensure the PLC is connected and reachable.")
    
    return plc_ip

def block_command_messages(plc_ip):
    # Define a callback function to filter and drop command messages
    def packet_callback(packet):
        if packet.haslayer(IP) and packet[IP].dst == plc_ip:
            if packet.haslayer(TCP) or packet.haslayer(UDP):
                print(f"Blocking command message to PLC at {plc_ip}")
                return  # Drop the packet
    
    # Start sniffing the network traffic
    print(f"Blocking command messages to PLC at {plc_ip}...")
    sniff(filter=f"host {plc_ip}", prn=packet_callback, store=0)

if __name__ == "__main__":
    try:
        plc_ip = find_plc_ip()
        print(f"PLC IP address found: {plc_ip}")
        block_command_messages(plc_ip)
    except Exception as e:
        print(f"Error: {e}")