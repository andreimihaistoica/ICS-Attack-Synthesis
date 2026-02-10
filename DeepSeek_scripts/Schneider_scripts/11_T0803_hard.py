import os
import re
import subprocess
from scapy.all import ARP, Ether, srp

def find_plc_ip():
    """
    Scan the network to find the PLC's IP address based on its MAC address.
    Replace '00:00:00:00:00:00' with the actual MAC address of the PLC if known.
    """
    target_mac = "00:00:00:00:00:00"  # Replace with the PLC's MAC address
    ip_range = "192.168.9.1/24"        # Adjust based on your network

    # Create an ARP request packet
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    # Send the packet and receive the response
    result = srp(packet, timeout=2, verbose=0)[0]

    # Parse the response to find the PLC's IP
    for sent, received in result:
        if received.hwsrc == target_mac:
            return received.psrc

    return None

def block_plc_commands(plc_ip):
    """
    Block command messages to the PLC by adding a firewall rule.
    """
    try:
        # Add a firewall rule to block all traffic to the PLC's IP
        rule = f"netsh advfirewall firewall add rule name='Block_PLC_Traffic' dir=in action=block remoteip={plc_ip} protocol=any"
        subprocess.run(rule, shell=True, check=True)
        print(f"Successfully blocked command messages to PLC at IP: {plc_ip}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to block command messages: {e}")

def main():
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    if not plc_ip:
        print("PLC IP address not found. Ensure the PLC is connected to the network.")
        return

    print(f"PLC IP address found: {plc_ip}")

    # Step 2: Block command messages to the PLC
    block_plc_commands(plc_ip)

if __name__ == "__main__":
    main()