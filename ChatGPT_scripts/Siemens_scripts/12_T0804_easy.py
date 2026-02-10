import scapy.all as scapy
import subprocess
import re

def find_plc_ip(subnet="192.168.1.0/24"):
    """
    Scan network to identify PLC device by checking for an open Modbus TCP (Port 502)
    """
    print("[*] Scanning network for PLC...")
    answered, _ = scapy.srp(scapy.Ether(dst="ff:ff:ff:ff:ff:ff") / scapy.ARP(pdst=subnet), timeout=3, verbose=False)

    for sent, received in answered:
        ip = received.psrc
        # Check if Port 502 (Modbus) is open
        print(f"[*] Checking IP {ip} for Modbus TCP (Port 502)")
        result = subprocess.run(["nmap", "-p", "502", ip], capture_output=True, text=True)
        if "open" in result.stdout:
            print(f"[+] PLC found at IP: {ip}")
            return ip

    print("[!] No PLC found.")
    return None

def block_plc_traffic(plc_ip):
    """
    Block all traffic to/from the identified PLC using Windows Firewall
    """
    if plc_ip:
        print(f"[*] Blocking traffic to/from PLC at {plc_ip}...")
        firewall_command = f'netsh advfirewall firewall add rule name="Block PLC" dir=in action=block remoteip={plc_ip}'
        subprocess.run(firewall_command, shell=True, check=True)
        
        firewall_command_out = f'netsh advfirewall firewall add rule name="Block PLC" dir=out action=block remoteip={plc_ip}'
        subprocess.run(firewall_command_out, shell=True, check=True)

        print("[+] Reporting messages to PLC have been blocked.")

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        block_plc_traffic(plc_ip)
    else:
        print("[!] No PLC detected, aborting.")