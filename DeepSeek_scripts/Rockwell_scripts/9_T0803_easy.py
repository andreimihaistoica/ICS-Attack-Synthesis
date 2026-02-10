import os
import re
import subprocess
import platform

def discover_plc_ip():
    """
    Discovers the IP address of the PLC on the network.
    This function uses arp-scan or nmap to discover devices on the network.
    """
    print("Discovering PLC IP address...")
    
    # Check the operating system to use the appropriate network scanning tool
    if platform.system() == "Windows":
        # Use arp -a to list devices on the network
        result = subprocess.run(["arp", "-a"], capture_output=True, text=True)
        devices = result.stdout.splitlines()
        
        # Filter out the PLC's IP address (assuming the PLC has a known MAC address prefix)
        for device in devices:
            if "00:1D:9C" in device:  # Example MAC address prefix for a PLC
                ip_match = re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', device)
                if ip_match:
                    plc_ip = ip_match.group(0)
                    print(f"PLC IP address found: {plc_ip}")
                    return plc_ip
    else:
        # Use nmap to scan the network for devices
        result = subprocess.run(["nmap", "-sn", "192.168.1.0/24"], capture_output=True, text=True)
        devices = result.stdout.splitlines()
        
        # Filter out the PLC's IP address (assuming the PLC has a known MAC address prefix)
        for device in devices:
            if "00:1D:9C" in device:  # Example MAC address prefix for a PLC
                ip_match = re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', device)
                if ip_match:
                    plc_ip = ip_match.group(0)
                    print(f"PLC IP address found: {plc_ip}")
                    return plc_ip
    
    print("PLC IP address not found.")
    return None

def block_command_messages(plc_ip):
    """
    Blocks command messages to the PLC using a firewall rule.
    """
    print(f"Blocking command messages to PLC at {plc_ip}...")
    
    # Check the operating system to use the appropriate firewall command
    if platform.system() == "Windows":
        # Use netsh to block traffic to the PLC's IP address
        subprocess.run(["netsh", "advfirewall", "firewall", "add", "rule", "name=Block_PLC_Commands", "dir=in", "action=block", "remoteip=" + plc_ip])
        print("Firewall rule added to block command messages.")
    else:
        # Use iptables to block traffic to the PLC's IP address
        subprocess.run(["iptables", "-A", "INPUT", "-s", plc_ip, "-j", "DROP"])
        print("Iptables rule added to block command messages.")

def main():
    # Step 1: Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    
    if plc_ip:
        # Step 2: Block command messages to the PLC
        block_command_messages(plc_ip)
    else:
        print("Unable to block command messages: PLC IP address not found.")

if __name__ == "__main__":
    main()