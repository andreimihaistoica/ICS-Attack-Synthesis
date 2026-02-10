from scapy.all import ARP, Ether, srp
from opcua import Client
import time

def find_plc_ip(target_mac):
    print("[*] Scanning network for PLC...")
    # Create an ARP request packet to scan the network
    arp = ARP(pdst="192.168.1.0/24")  # Adjust the network range as needed
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    # Send the packet and receive responses
    result = srp(packet, timeout=2, verbose=0)[0]

    # Parse the responses
    for sent, received in result:
        if received.hwsrc.lower() == target_mac.lower():
            print(f"[+] Found PLC with MAC {target_mac} at IP {received.psrc}")
            return received.psrc

    print("[-] PLC not found on the network.")
    return None

def collect_data_from_plc(plc_ip):
    print(f"[*] Connecting to PLC at {plc_ip}...")
    try:
        # Create an OPC UA client and connect to the PLC
        client = Client(f"opc.tcp://{plc_ip}:4840")
        client.connect()

        # Browse the OPC UA server to enumerate nodes
        root = client.get_root_node()
        print("[+] Connected to OPC UA server. Enumerating nodes...")
        nodes = root.get_children()

        # Collect data from the nodes
        for node in nodes:
            print(f"Node ID: {node.nodeid}, Display Name: {node.get_display_name().Text}")

        # Disconnect from the PLC
        client.disconnect()
        print("[*] Disconnected from PLC.")
    except Exception as e:
        print(f"[-] Error connecting to PLC: {e}")

if __name__ == "__main__":
    # Specify the MAC address of the PLC (replace with the actual MAC)
    plc_mac = "00:1A:2B:3C:4D:5E"  # Example MAC address

    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip(plc_mac)

    if plc_ip:
        # Step 2: Collect data from the PLC using OPC UA
        collect_data_from_plc(plc_ip)
    else:
        print("[-] Cannot proceed without PLC IP address.")