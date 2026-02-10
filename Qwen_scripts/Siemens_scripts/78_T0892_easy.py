import nmap
import paramiko
import time

# Function to discover the PLC's IP address
def discover_plc_ip():
    nm = nmap.PortScanner()
    nm.scan('192.168.1.0/24', arguments='-p 502')  # Adjust the subnet and port as needed
    for host in nm.all_hosts():
        if nm[host].has_tcp(502) and nm[host]['tcp'][502]['state'] == 'open':
            return host
    return None

# Function to change the PLC's credentials
def change_plc_credentials(ip, username, password, new_password):
    try:
        # Connect to the PLC using SSH
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, username=username, password=password)

        # Change the password
        stdin, stdout, stderr = client.exec_command(f'echo -e "{password}\n{new_password}\n{new_password}" | passwd {username}')
        time.sleep(2)  # Wait for the command to execute

        # Check if the password change was successful
        if 'password updated successfully' in stdout.read().decode():
            print(f"Password for user {username} on PLC {ip} has been changed successfully.")
        else:
            print(f"Failed to change password for user {username} on PLC {ip}.")

        client.close()
    except Exception as e:
        print(f"Error: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        print(f"PLC found at IP address: {plc_ip}")
    else:
        print("PLC not found on the network.")
        return

    # Define the credentials
    username = 'admin'  # Default username
    password = 'default_password'  # Default password
    new_password = 'new_secure_password'  # New password

    # Change the PLC's credentials
    change_plc_credentials(plc_ip, username, password, new_password)

if __name__ == "__main__":
    main()