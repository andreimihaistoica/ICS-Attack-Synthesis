from scapy.all import *
from pycomm3 import LogixDriver

def find_plc_ip():
    print("[+] Scanning for PLCs on the network...")

    # Define the broadcast address for Ethernet/IP
    broadcast_ip = "255.255.255.255"
    udp_port = 44818  # Common for Ethernet/IP

    # Send an Ethernet/IP discovery packet
    discovery_packet = IP(dst=broadcast_ip) / UDP(dport=udp_port) / Raw(load=b"\x63\x00\x00\x00")
    ans, _ = sr(discovery_packet, timeout=3, verbose=False)

    for sent, received in ans:
        if received.haslayer(IP) and received.haslayer(UDP):
            plc_ip = received[IP].src
            print(f"[+] Found PLC at IP: {plc_ip}")
            return plc_ip

    print("[-] No PLC found.")
    return None

def collect_plc_data(plc_ip):
    print(f"[+] Connecting to PLC at {plc_ip}")
    
    # Using pycomm3 to communicate with the PLC
    try:
        with LogixDriver(plc_ip) as plc:
            # Collect controller information
            controller_info = plc.get_plc_info()
            print(f"[+] Controller Info: {controller_info}")

            # Collect tag list
            tags = plc.get_tag_list()
            print("[+] Retrieved Tags:")
            for tag in tags:
                print(f"    - {tag['tag_name']} ({tag['tag_type']})")

            # Read key data points
            for tag in tags[:5]:  # Read first 5 tags for demonstration
                tag_name = tag["tag_name"]
                tag_value = plc.read(tag_name)
                print(f"[+] {tag_name}: {tag_value}")

    except Exception as e:
        print(f"[-] Error communicating with PLC: {e}")

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        collect_plc_data(plc_ip)