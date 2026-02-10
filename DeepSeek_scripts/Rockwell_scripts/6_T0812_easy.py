import os
import re
import subprocess
import paramiko

def discover_plc_ip():
    # Use ARP scan to discover devices in the network
    print("Scanning network for PLC...")
    arp_scan = subprocess.run(["arp", "-a"], capture_output=True, text=True)
    arp_output = arp_scan.stdout

    # Regex to match IP addresses (simplified for demonstration)
    ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    ip_addresses = re.findall(ip_pattern, arp_output)

    # Assuming the PLC's IP is known or can be identified in some way
    # For demonstration, let's assume the PLC's IP is the first one found
    if ip_addresses:
        plc_ip = ip_addresses[0]
        print(f"Found PLC IP: {plc_ip}")
        return plc_ip
    else:
        print("No PLC IP found.")
        return None

def attempt_default_login(ip):
    # Default credentials (example values)
    default_username = "admin"
    default_password = "admin"

    # Try to SSH into the PLC using default credentials
    try:
        print(f"Attempting to log in to {ip} with default credentials...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip, username=default_username, password=default_password)
        print("Login successful!")
        # Execute commands or further actions here
        ssh.close()
    except paramiko.AuthenticationException:
        print("Login failed: Invalid credentials.")
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    plc_ip = discover_plc_ip()
    if plc_ip:
        attempt_default_login(plc_ip)
    else:
        print("Could not proceed without PLC IP.")

if __name__ == "__main__":
    main()