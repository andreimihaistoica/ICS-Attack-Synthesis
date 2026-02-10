import socket
import paramiko

# Function to discover the PLC's IP address
def discover_plc_ip(subnet):
    # Example subnet: '192.168.1.'
    for i in range(1, 255):
        ip = subnet + str(i)
        try:
            socket.create_connection((ip, 44818), timeout=1)
            print(f"Found PLC at IP: {ip}")
            return ip
        except (socket.timeout, ConnectionRefusedError):
            continue
    print("PLC not found on the subnet.")
    return None

# Function to attempt default credentials
def attempt_default_credentials(ip, default_username, default_password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(ip, username=default_username, password=default_password)
        print(f"Successfully logged in with default credentials: {default_username}/{default_password}")
        # Here you can execute commands or perform actions
        ssh.close()
        return True
    except paramiko.AuthenticationException:
        print(f"Failed to authenticate with default credentials: {default_username}/{default_password}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

# Main script
if __name__ == "__main__":
    subnet = '192.168.1.'  # Adjust the subnet based on your network
    default_username = 'admin'  # Example default username
    default_password = 'password'  # Example default password

    plc_ip = discover_plc_ip(subnet)
    if plc_ip:
        attempt_default_credentials(plc_ip, default_username, default_password)