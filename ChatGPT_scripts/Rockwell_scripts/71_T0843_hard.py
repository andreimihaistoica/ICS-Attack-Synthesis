import scapy.all as scapy
from pycomm3 import LogixDriver
import time

def find_rockwell_plc():
    """Find Rockwell PLC on the local network using Ethernet/IP discovery."""
    print("[*] Scanning network for Rockwell Automation PLC...")
    
    # Create Ethernet/IP discovery packet
    packet = scapy.IP(dst="255.255.255.255") / scapy.UDP(sport=44818, dport=44818)
    response = scapy.sr1(packet, timeout=5, verbose=False)

    if response:
        plc_ip = response.src
        print(f"[+] Found Rockwell PLC at {plc_ip}")
        return plc_ip
    else:
        print("[-] No PLC found on the network.")
        return None

def perform_program_download(plc_ip):
    """Connect to the Rockwell PLC and perform a program download (requires appropriate permissions)."""
    print("[*] Attempting to connect to PLC...")

    with LogixDriver(plc_ip) as plc:
        if plc.connected:
            print("[+] Successfully connected to PLC!")

            # Example: Read controller properties to ensure it's accessible
            properties = plc.get_plc_info()
            print("[*] PLC Properties:", properties)

            # Example: Simulating an online edit or program change
            print("[*] Initiating program download...")

            # This is a placeholder. Actual program download requires vendor-specific tools such as Rockwell’s RSLinx or Studio 5000 API.
            try:
                plc.write_tag('START', True)  # Example of modifying a PLC tag
                print("[+] Program modification successful (simulated).")
            except Exception as e:
                print(f"[-] Error modifying PLC program: {e}")
        else:
            print("[-] Failed to connect to PLC.")

def main():
    plc_ip = find_rockwell_plc()

    if plc_ip:
        perform_program_download(plc_ip)
    else:
        print("[-] Could not identify PLC IP. Aborting...")

if __name__ == "__main__":
    main()