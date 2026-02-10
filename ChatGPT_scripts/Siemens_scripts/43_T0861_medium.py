import snap7
import time
from snap7.util import get_int, get_real, get_string
from scapy.all import ARP, Ether, srp


def find_plc_ip():
    """Scan the local network to find the Siemens S7-1200 PLC IP address."""
    print("[+] Scanning network for Siemens PLC...")
    
    # Define network range (adjust if needed)
    target_ip_range = "192.168.1.1/24"

    # Create an ARP request packet
    arp = ARP(pdst=target_ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    # Send the packet and get responses
    result = srp(packet, timeout=3, verbose=False)[0]

    for sent, received in result:
        if received.hwsrc.startswith("00:0E:8C"):  # Siemens MAC vendor prefix
            print(f"[+] PLC found at IP: {received.psrc}")
            return received.psrc  

    print("[-] No Siemens PLC found on the network.")
    return None


def read_plc_tags(plc_ip):
    """Connects to the PLC and reads tag/point values."""
    plc = snap7.client.Client()
    
    try:
        print(f"[+] Connecting to PLC at {plc_ip}...")
        plc.connect(plc_ip, 0, 1)  # Rack = 0, Slot = 1 for S7-1200

        if plc.get_connected():
            print("[+] Successfully connected to the PLC.")

            # Example: Read Data Block 1 (DB1) to extract possible tag data
            db_number = 1
            size = 256  # Adjust according to DB size
            data = plc.db_read(db_number, 0, size)

            # Extract potential tag values
            tag_1 = get_int(data, 0)      # Read integer at byte 0
            tag_2 = get_real(data, 2)     # Read floating-point at byte 2
            tag_3 = get_string(data, 6, 10)  # Read string at byte 6, length 10

            print("\n[+] Extracted PLC Point & Tag Values:")
            print(f"    - Integer Value (Tag 1): {tag_1}")
            print(f"    - Real Value (Tag 2): {tag_2}")
            print(f"    - String Value (Tag 3): {tag_3}")

        else:
            print("[-] Connection to PLC failed.")

    except Exception as e:
        print(f"[ERROR] {e}")

    finally:
        plc.disconnect()


# Main Execution
if __name__ == "__main__":
    plc_ip = find_plc_ip()

    if plc_ip:
        read_plc_tags(plc_ip)
    else:
        print("[-] Could not find PLC IP. Exiting...")