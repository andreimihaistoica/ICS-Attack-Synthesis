import scapy.all as scapy
import psutil
import time

def discover_plc_ip():
    # Send an ARP request to discover devices on the network
    arp_request = scapy.ARP(pdst="192.168.1.0/24")
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    # Filter and print the IP and MAC addresses of discovered devices
    for element in answered_list:
        print(f"IP: {element[1].psrc} - MAC: {element[1].hwsrc}")

def monitor_network_traffic():
    # Monitor network traffic and print details of packets
    while True:
        packets = scapy.sniff(count=10, filter="ip")
        for packet in packets:
            if packet.haslayer(scapy.IP):
                ip_layer = packet[scapy.IP]
                print(f"Source IP: {ip_layer.src} - Destination IP: {ip_layer.dst}")
        time.sleep(5)

if __name__ == "__main__":
    print("Discovering PLC IP address...")
    discover_plc_ip()
    print("Monitoring network traffic...")
    monitor_network_traffic()