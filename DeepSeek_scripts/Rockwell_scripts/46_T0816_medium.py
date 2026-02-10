import os
import sys
from pycomm3 import LogixDriver
from ipaddress import ip_network
from socket import gethostbyname, gaierror

def discover_plc_ip(network_range):
    """Scan the network to find the PLC's IP address."""
    for ip in ip_network(network_range).hosts():
        ip_str = str(ip)
        try:
            # Attempt to connect to the PLC
            with LogixDriver(ip_str) as plc:
                if plc.get_plc_name():
                    print(f"PLC found at IP: {ip_str}")
                    return ip_str
        except Exception as e:
            print(f"Scanning {ip_str}: {e}")
    return None

def force_plc_restart(plc_ip):
    """Force a restart or shutdown of the PLC."""
    try:
        with LogixDriver(plc_ip) as plc:
            # Send a command to restart the PLC
            # This is a placeholder command; actual command may vary based on PLC model and firmware
            plc.write_tag('Program:MainProgram.RestartCommand', 1)
            print("PLC restart command sent.")
    except Exception as e:
        print(f"Failed to restart PLC: {e}")

def main():
    # Define the network range to scan (e.g., '192.168.1.0/24')
    network_range = '192.168.1.0/24'
    
    # Step 1: Discover PLC IP address
    plc_ip = discover_plc_ip(network_range)
    if not plc_ip:
        print("PLC not found in the specified network range.")
        sys.exit(1)
    
    # Step 2: Force PLC restart
    force_plc_restart(plc_ip)

if __name__ == "__main__":
    main()