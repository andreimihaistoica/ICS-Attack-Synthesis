import snap7
import socket
import time
import subprocess
import platform
import re

# Configuration (Adjust these as needed, if direct IP is known)
PLC_IP = None  # Leave as None if you want the script to discover the IP
PLC_RACK = 0
PLC_SLOT = 1
POLLING_INTERVAL = 5  # seconds between checks
SHUTDOWN_COMMAND = "shutdown /s /t 1" # Windows shutdown command. Adapt for other OS.

def find_plc_ip():
    """
    Attempts to find the PLC's IP address by scanning the network.
    This is a basic implementation and may need to be adapted for your specific network setup.
    It relies on pinging a potential IP range and checking for a response with a certain TTL.

    Returns:
        str: The PLC's IP address, or None if not found.
    """
    print("Attempting to discover PLC IP...")
    # Adjust the IP range to suit your network
    base_ip = "192.168.1." # Replace with the first three octets of your network
    for i in range(1, 255):
        ip = base_ip + str(i)
        try:
            if platform.system().lower() == "windows":
                result = subprocess.run(["ping", "-n", "1", "-w", "500", ip], capture_output=True, text=True)
                # Check for a successful ping and a low TTL (often indicating a local device)
                if result.returncode == 0 and "TTL=" in result.stdout:
                    ttl_match = re.search(r"TTL=(\d+)", result.stdout)
                    if ttl_match and int(ttl_match.group(1)) < 64:  # Adjust TTL threshold if needed
                        print(f"Found potential PLC at: {ip}")
                        return ip

            else: #linux or mac
                result = subprocess.run(["ping", "-c", "1", "-w", "0.5", ip], capture_output=True, text=True)
                if result.returncode == 0 and "ttl=" in result.stdout:
                    ttl_match = re.search(r"ttl=(\d+)", result.stdout)
                    if ttl_match and int(ttl_match.group(1)) < 64:
                        print(f"Found potential PLC at: {ip}")
                        return ip

        except Exception as e:
            print(f"Error pinging {ip}: {e}")

    print("PLC IP address not found.")
    return None

def check_plc_connection(ip_address, rack, slot):
    """
    Checks if a connection can be established with the PLC.

    Returns:
        bool: True if connection is successful, False otherwise.
    """
    try:
        plc = snap7.client.Client()
        plc.connect(ip_address, rack, slot)
        plc.disconnect()
        return True
    except Exception as e:
        print(f"Error connecting to PLC at {ip_address}: {e}")
        return False



def restart_windows_machine():
    """
    Restarts the Windows machine.
    """
    print("Executing shutdown command...")
    try:
        subprocess.run(SHUTDOWN_COMMAND, shell=True, check=True)
        print("Shutdown command executed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing shutdown command: {e}")

def main():

    global PLC_IP  # Use global scope for potential IP discovery

    if PLC_IP is None:
        PLC_IP = find_plc_ip()
        if PLC_IP is None:
            print("Unable to find PLC IP.  Exiting.")
            return


    print(f"Using PLC IP: {PLC_IP}")


    while True:
        try:
            if not check_plc_connection(PLC_IP, PLC_RACK, PLC_SLOT):
                print("PLC connection failed. Attempting restart...")
                restart_windows_machine()  # Immediately attempt restart on connection failure
                break # Exit the loop after attempting the restart.  Otherwise, it will restart repeatedly.
            else:
                print("PLC is connected and running.  Waiting...")
                time.sleep(POLLING_INTERVAL)


        except KeyboardInterrupt:
            print("Script interrupted. Exiting...")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            break # Exit on unexpected errors


if __name__ == "__main__":
    main()