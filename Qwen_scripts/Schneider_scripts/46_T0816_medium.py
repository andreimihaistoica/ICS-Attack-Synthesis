import socket
import subprocess
import time
from scapy.all import ARP, Ether, srp

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the IP range to scan (adjust as needed)
    ip_range = "192.168.1.0/24"
    
    # Create an ARP request packet
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and capture the response
    result = srp(packet, timeout=2, verbose=False)[0]

    # Parse the response
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    # Filter the devices to find the PLC (assuming the PLC has a specific MAC address or other identifier)
    plc_ip = None
    for device in devices:
        # Example: Assuming the PLC has a specific MAC address
        if device['mac'] == '00:11:22:33:44:55':
            plc_ip = device['ip']
            break

    if plc_ip:
        print(f"PLC found at IP: {plc_ip}")
    else:
        print("PLC not found in the network.")
    
    return plc_ip

# Function to send a restart command to the PLC
def restart_plc(plc_ip):
    if not plc_ip:
        print("PLC IP address not found. Cannot proceed with restart.")
        return

    # Example command to restart the PLC (this is a placeholder and should be replaced with the actual command)
    # For Schneider Electric TM221CE16R, you might need to use a specific protocol or tool to send the command
    # This example uses a hypothetical command
    command = f"plc_restart {plc_ip}"

    try:
        # Execute the command
        subprocess.run(command, shell=True, check=True)
        print(f"Restart command sent to PLC at IP: {plc_ip}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to send restart command: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()

    # Send the restart command
    restart_plc(plc_ip)

if __name__ == "__main__":
    main()