import scapy.all as scapy  # For network scanning to discover PLC IP
from pycomm3 import LogixDriver  # For communicating with an Allen-Bradley PLC
import time

# Function to find the PLC's IP address by scanning the network
def find_plc_ip(network_range="192.168.1.0/24"):
    print("[*] Scanning network for PLC devices...")
    arp_request = scapy.ARP(pdst=network_range)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]

    for element in answered_list:
        ip = element[1].psrc
        mac = element[1].hwsrc
        print(f"[*] Found device - IP: {ip} | MAC: {mac}")

        # You might refine this logic to filter known PLC MAC addresses or patterns
        return ip  # Return first found device (assuming it's the PLC)

    print("[!] No PLC detected.")
    return None

# Function to detect the operation mode of a Logix PLC
def detect_plc_mode(plc_ip):
    try:
        print(f"[*] Connecting to PLC at {plc_ip}...")
        with LogixDriver(plc_ip) as plc:
            mode = plc.get_plc_mode()  
            if mode:
                print(f"[+] PLC is currently in {mode.upper()} mode.")
            else:
                print("[!] Failed to retrieve PLC mode.")
    except Exception as e:
        print(f"[!] Error communicating with PLC: {str(e)}")

# Main execution
if __name__ == "__main__":
    plc_ip = find_plc_ip()  # Determine the PLC's IP address
    if plc_ip:
        time.sleep(2)  # Short delay before connecting
        detect_plc_mode(plc_ip)  # Detect the operating mode