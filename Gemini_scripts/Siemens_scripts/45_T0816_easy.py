import socket
import subprocess
import time
import os

# Configuration - Adapt these values based on your PLC and network
SWITCH_IP = "YOUR_SWITCH_IP"  # e.g., "192.168.1.10"
SWITCH_USERNAME = "YOUR_SWITCH_USERNAME" # e.g., "admin"
SWITCH_PASSWORD = "YOUR_SWITCH_PASSWORD" # e.g., "password"
PLC_DEFAULT_IP_RANGE_START = "192.168.1.1" # Example: PLC IP addresses might fall within this range
PLC_DEFAULT_IP_RANGE_END = "192.168.1.254" # Example
PLC_PORT = 502  # Example:  Modbus TCP port (common for PLCs) or other relevant port
RESTART_DELAY = 5  # Seconds to wait after sending the restart command

def find_plc_ip(ip_range_start, ip_range_end, port):
    """
    Scans the network for the PLC based on port. This is a basic example and may need adaptation.
    This method uses ping and port scanning to find possible PLC IP addresses.
    Consider more robust detection methods if needed (e.g., identifying PLC-specific protocols).
    """
    start_ip_parts = list(map(int, ip_range_start.split('.')))
    end_ip_parts = list(map(int, ip_range_end.split('.')))

    if len(start_ip_parts) != 4 or len(end_ip_parts) != 4:
        print("Invalid IP address format.")
        return None

    start_ip_int = (start_ip_parts[0] << 24) | (start_ip_parts[1] << 16) | (start_ip_parts[2] << 8) | start_ip_parts[3]
    end_ip_int = (end_ip_parts[0] << 24) | (end_ip_parts[1] << 16) | (end_ip_parts[2] << 8) | end_ip_parts[3]

    possible_ips = []

    for ip_int in range(start_ip_int, end_ip_int + 1):
        ip_parts = [(ip_int >> (8 * i)) & 0xFF for i in range(3, -1, -1)]
        ip_address = ".".join(map(str, ip_parts))

        # Ping the IP address.  A positive ping indicates a live host.
        try:
            ping_reply = subprocess.run(["ping", "-n", "1", "-w", "100", ip_address], capture_output=True, timeout=0.2) # reduced timeout
            if ping_reply.returncode == 0: #ping was successful
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.2)
                    result = sock.connect_ex((ip_address, port)) # very short timeout
                    if result == 0:
                        print(f"Found a service at {ip_address}:{port}")
                        possible_ips.append(ip_address)
                    sock.close()
                except socket.timeout:
                    print(f"Connection timeout to {ip_address}:{port}")
                except Exception as e:
                    print(f"Error connecting to {ip_address}:{port}: {e}")

        except subprocess.TimeoutExpired:
            print(f"Ping timed out for {ip_address}")
        except Exception as e:
            print(f"Error pinging {ip_address}: {e}")

    if possible_ips:
        print("Possible PLC IP addresses:", possible_ips) # show possible targets to user
        return possible_ips[0] # return the first IP found
    else:
        print("No PLC IP address found in the specified range and port.")
        return None


def restart_plc_via_switch(plc_ip, switch_ip, switch_username, switch_password):
    """
    Restarts the PLC by disabling and re-enabling the switch port it's connected to.

    Note:  This is a simplified example.  Real-world switches often require more complex
    authentication and command structures.  This implementation may not work directly
    and requires adaptation for your specific switch model and configuration.  Using SSH
    and a library like `netmiko` (or the switch's API if available) is generally recommended.

    Important:  This code assumes you know which port the PLC is connected to on the switch.
    You'll need to determine this manually or through switch management tools.  Damage could
    result if the incorrect port is specified.
    """

    # *IMPORTANT*: Replace 'YOUR_PLC_SWITCH_PORT' with the correct port number.
    # The script will not run without you specifying this.
    PLC_SWITCH_PORT = "YOUR_PLC_SWITCH_PORT"

    if PLC_SWITCH_PORT == "YOUR_PLC_SWITCH_PORT":
        print("Error: Please configure the PLC switch port number in the script. Exiting.")
        return False


    try:
        # Construct SSH command (example using `sshpass` - highly discouraged in production!)
        # Consider using SSH keys for passwordless authentication instead.
        # Replace with appropriate commands for your switch model (e.g., using `netmiko`).
        # ***THIS IS A SIMPLIFIED EXAMPLE and MAY REQUIRE ADAPTATION***

        command_disable = f'sshpass -p "{switch_password}" ssh {switch_username}@{switch_ip} "configure terminal; interface {PLC_SWITCH_PORT}; shutdown; end"'
        command_enable = f'sshpass -p "{switch_password}" ssh {switch_username}@{switch_ip} "configure terminal; interface {PLC_SWITCH_PORT}; no shutdown; end"'

        print(f"Disabling port {PLC_SWITCH_PORT} on switch {switch_ip}...")
        result_disable = subprocess.run(command_disable, shell=True, capture_output=True, text=True)

        if result_disable.returncode != 0:
            print(f"Error disabling port: {result_disable.stderr}")
            return False
        else:
            print(f"Port {PLC_SWITCH_PORT} disabled successfully.")

        time.sleep(RESTART_DELAY)  # Wait a short period

        print(f"Enabling port {PLC_SWITCH_PORT} on switch {switch_ip}...")
        result_enable = subprocess.run(command_enable, shell=True, capture_output=True, text=True)

        if result_enable.returncode != 0:
            print(f"Error enabling port: {result_enable.stderr}")
            return False
        else:
            print(f"Port {PLC_SWITCH_PORT} enabled successfully.")

        print(f"PLC restart initiated via switch port cycling.")
        return True


    except Exception as e:
        print(f"An error occurred: {e}")
        return False

if __name__ == "__main__":

    # 1. Find PLC IP Address (if needed)
    PLC_IP = find_plc_ip(PLC_DEFAULT_IP_RANGE_START, PLC_DEFAULT_IP_RANGE_END, PLC_PORT)


    if not PLC_IP:
        print("PLC IP address not found.  Please manually configure PLC_IP or adjust the scanning range.")
        PLC_IP = input("Enter PLC IP Address: ")  # Prompt the user to input the PLC IP address
        if not PLC_IP:
            print("No PLC IP address provided. Exiting.")
            exit()

    # 2. Restart PLC via switch port cycling
    success = restart_plc_via_switch(PLC_IP, SWITCH_IP, SWITCH_USERNAME, SWITCH_PASSWORD)

    if success:
        print("PLC restart process completed (potentially successfully, check PLC status).")
    else:
        print("PLC restart process failed.")