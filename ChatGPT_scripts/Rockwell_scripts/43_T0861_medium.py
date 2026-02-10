from scapy.all import ARP, Ether, srp
from pycomm3 import LogixDriver
import socket

def find_plc_ip(network_range="192.168.1.0/24"):
    """
    Scans the network to find the IP address of a Rockwell Micro850 PLC.
    Returns the first identified PLC IP address.
    """
    print("[*] Scanning the network for Micro850 PLC...")
    
    # Create an ARP request packet
    arp_request = ARP(pdst=network_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp_request

    # Send the request and capture the response
    answered, _ = srp(packet, timeout=2, verbose=False)

    for send, recv in answered:
        try:
            # Try connecting to the possible PLC IP
            ip = recv.psrc
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)
            result = s.connect_ex((ip, 44818))  # EtherNet/IP Port 44818
            s.close()

            if result == 0:
                print(f"[+] Found PLC at {ip}")
                return ip
        except Exception as e:
            continue

    print("[!] No PLC found on the network range.")
    return None

def collect_tags(plc_ip):
    """
    Connects to the Micro850 PLC and retrieves all available tags.
    """
    try:
        print(f"[*] Connecting to PLC at {plc_ip}...")
        with LogixDriver(plc_ip) as plc:
            tags = plc.get_tag_list()
            if tags:
                print("[+] Retrieved the following tags from the PLC:")
                for tag in tags:
                    print(f"    - {tag}")
            else:
                print("[!] No tags found on the PLC.")

    except Exception as e:
        print(f"[!] Failed to retrieve tags: {e}")

if __name__ == "__main__":
    # Step 1: Auto-discover Micro850 PLC IP
    plc_ip = find_plc_ip()

    # Step 2: Collect tag information if PLC is located
    if plc_ip:
        collect_tags(plc_ip)