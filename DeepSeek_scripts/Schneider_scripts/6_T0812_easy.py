import paramiko
from scapy.all import ARP, Ether, srp

# Default credentials for the PLC
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "admin"

# Function to discover the PLC's IP address using ARP scan
def discover_plc_ip():
    # Define the network to scan (e.g., "192.168.1.0/24")
    ip_range = "192.168.1.0/24"
    
    # Create ARP request packet
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and receive the response
    result = srp(packet, timeout=2, verbose=0)[0]

    # Parse the response to find the PLC's IP address
    plc_ip = None
    for sent, received in result:
        # Check if the device is a PLC (you can add more specific checks)
        if received.psrc.startswith("192.168.1."):
            plc_ip = received.psrc
            break

    return plc_ip

# Function to attempt login using default credentials
def attempt_login(ip, username, password):
    try:
        # Create an SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Attempt to connect to the PLC
        ssh.connect(ip, username=username, password=password, timeout=5)
        print(f"Successfully logged into {ip} with default credentials.")
        
        # Execute a command (e.g., list files in the root directory)
        stdin, stdout, stderr = ssh.exec_command("ls")
        print(stdout.read().decode())
        
        # Close the connection
        ssh.close()
    except Exception as e:
        print(f"Failed to login to {ip}: {e}")

# Main script
if __name__ == "__main__":
    # Step 1: Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    
    if plc_ip:
        print(f"Discovered PLC IP: {plc_ip}")
        
        # Step 2: Attempt to login using default credentials
        attempt_login(plc_ip, DEFAULT_USERNAME, DEFAULT_PASSWORD)
    else:
        print("PLC IP address not found.")