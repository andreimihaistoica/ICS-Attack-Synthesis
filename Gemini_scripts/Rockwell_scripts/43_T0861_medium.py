import pycomm3
import socket
import re
import subprocess
import time
from datetime import datetime

# Configuration
LOG_FILE = "point_tag_collection.log"
DEFAULT_PLC_IP = "192.168.1.10"  # A default IP if auto-discovery fails.  Adjust if needed.
AUTO_DISCOVER_TIMEOUT = 5 #seconds

def log_message(message):
    """Logs messages to a file with timestamps."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] {message}\n")
    print(f"[{timestamp}] {message}")  # Also print to console


def discover_plc_ip():
    """Attempts to discover the PLC's IP address using arp-scan.

    Returns:
        str: The PLC's IP address if found, None otherwise.
    """
    log_message("Attempting to discover PLC IP address...")
    try:
        # This requires arp-scan to be installed on the system.
        # On Debian/Ubuntu: sudo apt-get install arp-scan
        # Ensure arp-scan is in your system's PATH.

        # Specify your network interface if needed (e.g., eth0, wlan0)
        # If not, arp-scan will try to determine the correct interface.
        # interface = "eth0"
        # command = f"sudo arp-scan --interface={interface} --localnet"

        command = "sudo arp-scan --localnet"
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        start_time = time.time()
        while True:
            output, error = process.communicate()  # Capture output and errors
            return_code = process.returncode  # Get the return code after communicate()
            if return_code is not None or time.time() - start_time > AUTO_DISCOVER_TIMEOUT:  # Timeout
                 break

        output_str = output.decode("utf-8")
        error_str = error.decode("utf-8")

        if return_code == 0:  # arp-scan executed successfully
            for line in output_str.splitlines():
                if "Rockwell Automation" in line:  # Or a more specific identifier
                    parts = line.split()
                    if len(parts) > 1:
                        ip_address = parts[0]
                        log_message(f"Discovered PLC IP address: {ip_address}")
                        return ip_address
        else:
            log_message(f"arp-scan failed with error code {return_code}: {error_str}")
            log_message("Ensure arp-scan is installed and has necessary permissions (sudo).")

    except FileNotFoundError:
        log_message("arp-scan not found.  Please install it (e.g., 'sudo apt-get install arp-scan').")
    except Exception as e:
        log_message(f"Error during IP discovery: {e}")

    log_message("PLC IP address discovery failed.")
    return None


def get_plc_tags(plc_ip):
    """Retrieves tag information from the PLC.

    Args:
        plc_ip (str): The IP address of the Rockwell Micro850 PLC.

    Returns:
        dict: A dictionary containing tag names and their values.  Returns None on error.
    """
    try:
        with pycomm3.LogixDriver(plc_ip) as plc:
            plc.timeout = 5 #set timeout to 5 seconds
            tags = plc.get_tag_list()
            if tags is None:
                log_message(f"Failed to retrieve tag list from PLC at {plc_ip}.  Check connectivity and PLC configuration.")
                return None

            tag_data = {}
            for tag in tags:
                try:
                    read_result = plc.read(tag.tagName) #use .tagName instead of .symbolName
                    if read_result.status == "Success":
                        tag_data[tag.tagName] = read_result.value
                    else:
                        log_message(f"Failed to read tag {tag.tagName}: {read_result.status}")

                except Exception as e:
                    log_message(f"Error reading tag {tag.tagName}: {e}")

            return tag_data

    except pycomm3.exceptions.CommError as e:
        log_message(f"Communication error with PLC at {plc_ip}: {e}")
        return None
    except Exception as e:
        log_message(f"An unexpected error occurred: {e}")
        return None


def main():
    """Main function to discover IP (if needed) and collect tag information."""

    plc_ip = discover_plc_ip()
    if not plc_ip:
        log_message("Failed to automatically discover PLC IP address.  Using default.")
        plc_ip = DEFAULT_PLC_IP

    log_message(f"Using PLC IP address: {plc_ip}")

    tag_data = get_plc_tags(plc_ip)

    if tag_data:
        log_message("Successfully collected tag data:")
        for tag, value in tag_data.items():
            log_message(f"Tag: {tag}, Value: {value}")

        # Optional: Save tag data to a file (e.g., JSON, CSV) for later analysis.
        # Example using JSON:
        # import json
        # with open("tag_data.json", "w") as f:
        #     json.dump(tag_data, f, indent=4)
        log_message("Tag data collection complete.")
    else:
        log_message("Tag data collection failed.")


if __name__ == "__main__":
    main()