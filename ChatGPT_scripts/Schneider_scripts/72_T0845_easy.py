import snap7
from snap7.util import get_int
import scapy.all as scapy
import socket
import struct

def find_plc_ip(network_range="192.168.1.0/24"):
    print("[*] Scanning network for PLC devices...")

    # Perform an ARP scan to detect devices
    arp_request = scapy.ARP(pdst=network_range)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]
    plc_ip = None

    for answer in answered_list:
        ip = answer[1].psrc
        mac = answer[1].hwsrc
        print(f"Discovered device -> IP: {ip}, MAC: {mac}")

        # Attempt to identify PLC by checking port 102 (Siemens S7)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ip, 102))
        sock.close()

        if result == 0:
            print(f"[+] Found potential Siemens PLC at {ip}")
            plc_ip = ip
            break

    if not plc_ip:
        print("[-] No PLC detected!")
        exit()

    return plc_ip

def upload_plc_program(plc_ip):
    print(f"[*] Connecting to PLC at {plc_ip}...")
    
    client = snap7.client.Client()
    try:
        client.connect(plc_ip, 0, 1)  # Rack 0, Slot 1 (Typical for Siemens S7-1200/1500)
        if client.get_connected():
            print(f"[+] Connected to PLC at {plc_ip}")
            
            # Attempt to read memory (assuming DB1 holds configuration)
            db_number = 1  # Example DB number
            start = 0
            size = 256  # Read first 256 bytes
            data = client.db_read(db_number, start, size)
            
            # Save to a file
            with open("plc_program_backup.bin", "wb") as f:
                f.write(data)
                
            print(f"[+] Program uploaded successfully and saved as 'plc_program_backup.bin'")
        else:
            print("[-] Failed to connect to PLC.")
    
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        client.disconnect()

# Step 1: Find PLC IP Address
plc_ip = find_plc_ip()

# Step 2: Upload the Program from the PLC
upload_plc_program(plc_ip)