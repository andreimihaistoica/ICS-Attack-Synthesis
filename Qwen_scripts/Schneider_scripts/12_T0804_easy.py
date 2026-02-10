import scapy.all as scapy
import netifaces as ni
import time

# Function to discover the PLC's IP address
def discover_plc_ip(interface):
    # Send an ARP request to discover devices on the network
    arp_request = scapy.ARP(pdst="192.168.1.0/24")  # Adjust the subnet to match your network
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    # Filter the responses to find the PLC
    for element in answered_list:
        ip = element[1].psrc
        mac = element[1].hwsrc
        print(f"Found device: IP={ip}, MAC={mac}")
        # Add your logic to identify the PLC (e.g., based on MAC address or IP)
        if mac == "00:11:22:33:44:55":  # Replace with the actual PLC MAC address
            return ip
    return None

# Function to block reporting messages
def block_reporting_messages(plc_ip):
    # Define the interface to use for packet sniffing and sending
    interface = ni.gateways()['default'][ni.AF_INET][1]
    print(f"Using interface: {interface}")

    # Define the filter for sniffing reporting messages
    filter_str = f"ip host {plc_ip} and tcp port 502"  # Adjust the port if necessary

    # Start sniffing for reporting messages
    def packet_callback(packet):
        if packet.haslayer(scapy.IP) and packet[scapy.IP].src == plc_ip:
            print(f"Blocking reporting message from {plc_ip}")
            # Drop the packet by not forwarding it

    scapy.sniff(iface=interface, filter=filter_str, prn=packet_callback, store=0)

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip("eth0")  # Replace with your network interface
    if plc_ip:
        print(f"PLC IP address: {plc_ip}")
        # Block reporting messages
        block_reporting_messages(plc_ip)
    else:
        print("PLC not found on the network")

if __name__ == "__main__":
    main()