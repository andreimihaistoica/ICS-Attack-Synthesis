from pycomm3 import CIPDriver
from scapy.all import *
import time

# Function to find Rockwell PLC on the network
def find_plc():
    print("[*] Scanning for Rockwell PLC...")
    
    # EtherNet/IP uses UDP 44818 for discovery
    discover_packet = (
        b"\x63\x00\x00\x00" +  # Command (ListIdentity 0x0063)
        b"\x00\x00\x00\x00"  # Session Handle (0 for discovery)
    )

    responses = srp(
        IP(dst="255.255.255.255") / UDP(dport=44818, sport=44818) / Raw(load=discover_packet),
        timeout=3,
        verbose=False,
        multi=True
    )

    for _, resp in responses[0]:
        if resp.haslayer(Raw):
            print("[+] PLC Found! Extracting details...")
            plc_ip = resp[IP].src
            print(f"[+] PLC IP Address: {plc_ip}")
            return plc_ip

    print("[-] No PLC found on the network.")
    return None

# Function to collect Rockwell Micro850 PLC info
def collect_plc_info(plc_ip):
    print("[*] Attempting to retrieve information from PLC...")

    with CIPDriver(f"ethernet://{plc_ip}") as plc:
        if plc.connected:
            print("[+] Connected to the PLC!")
            
            # Example: Gather system name and CPU info
            system_name = plc.read("PROGRAM:MainProgram.SystemName")
            cpu_type = plc.read("PROGRAM:MainProgram.CPUType")
            serial_number = plc.read("PROGRAM:MainProgram.SerialNumber")

            # Print result
            print(f"[+] System Name: {system_name.value}")
            print(f"[+] CPU Type: {cpu_type.value}")
            print(f"[+] Serial Number: {serial_number.value}")
        else:
            print("[-] Failed to connect to the PLC.")

# Main Execution Flow
plc_ip = find_plc()
if plc_ip:
    collect_plc_info(plc_ip)