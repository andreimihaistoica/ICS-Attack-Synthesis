from scapy.all import ARP, Ether, srp
import subprocess
import re

def discover_plc_ip():
    # Define the IP range to scan (e.g., 192.168.1.0/24)
    ip_range = "192.168.1.0/24"
    
    # Create an ARP request packet
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and receive the response
    result = srp(packet, timeout=2, verbose=0)[0]

    # Extract the IP addresses from the response
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    # Assume the PLC has a known MAC address prefix (e.g., 00:80:9F)
    plc_mac_prefix = "00:80:9F"
    for device in devices:
        if device['mac'].startswith(plc_mac_prefix):
            return device['ip']

    return None

def block_plc_commands(plc_ip):
    # Block the PLC's IP address using Windows Firewall
    try:
        # Add a new inbound rule to block all traffic from the PLC's IP
        subprocess.run(
            ["netsh", "advfirewall", "firewall", "add", "rule", "name='Block PLC Commands'", 
             "dir=in", "action=block", "remoteip=" + plc_ip, "protocol=any", "enable=yes"],
            check=True
        )
        print(f"Successfully blocked command messages from PLC at IP: {plc_ip}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to block command messages from PLC: {e}")

def main():
    # Step 1: Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    
    if plc_ip:
        print(f"Discovered PLC IP address: {plc_ip}")
        
        # Step 2: Block command messages to the PLC
        block_plc_commands(plc_ip)
    else:
        print("Could not discover the PLC's IP address.")

if __name__ == "__main__":
    main()