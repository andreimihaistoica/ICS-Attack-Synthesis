import os
import subprocess
import socket
import sys

def find_plc_ip(network_prefix="192.168.1"):
    """Function to find the PLC's IP address in the local network."""
    for i in range(1, 255):
        ip = f"{network_prefix}.{i}"
        response = os.system(f"ping -c 1 {ip} > /dev/null 2>&1")
        if response == 0:
            try:
                hostname = socket.gethostbyaddr(ip)[0]
                if "PLC" in hostname.upper():  # Assuming the PLC has "PLC" in its hostname
                    return ip
            except socket.herror:
                continue
    return None

def restart_plc(ip):
    """Function to send a restart command to the PLC."""
    # This is a placeholder for the actual command to restart the PLC.
    # The command will depend on the specific PLC model and its API or CLI.
    # For example, using a REST API or SSH command.
    try:
        # Example using a REST API (replace with actual API call)
        # response = requests.post(f"http://{ip}/api/restart", auth=('user', 'password'))
        # if response.status_code == 200:
        #     print(f"PLC at {ip} restarted successfully.")
        # else:
        #     print(f"Failed to restart PLC at {ip}.")

        # Example using SSH (replace with actual SSH command)
        # ssh_command = f"ssh user@{ip} 'sudo reboot'"
        # subprocess.run(ssh_command, shell=True, check=True)
        # print(f"PLC at {ip} restarted successfully.")

        print(f"PLC at {ip} restart command sent. (Replace with actual command)")
    except Exception as e:
        print(f"Error restarting PLC at {ip}: {e}")

def main():
    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip()
    if not plc_ip:
        print("PLC IP address not found.")
        sys.exit(1)

    print(f"PLC found at IP: {plc_ip}")

    # Step 2: Send the restart command to the PLC
    restart_plc(plc_ip)

if __name__ == "__main__":
    main()