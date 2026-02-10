import snap7
import socket
import subprocess
import os
import time

# Configuration - ADJUST THESE BASED ON YOUR SETUP
PLC_IP_SCAN_RANGE = "192.168.1.0/24"  # Adjust to your network segment
PLC_RACK = 0
PLC_SLOT = 1
BACKUP_FILE = "plc_program_backup.bin" # Destination file to save the PLC's program

# -------------------------------------------------------------------------
# IP Address Scanning Function
# -------------------------------------------------------------------------
def find_plc_ip(ip_range):
    """
    Scans a network range to find the Schneider Electric TM221CE16R PLC.
    Relies on nmap being installed.

    Args:
        ip_range (str): The IP range to scan (e.g., "192.168.1.0/24").

    Returns:
        str: The IP address of the PLC if found, otherwise None.
    """

    try:
        # Use nmap to scan for devices with open Modbus port (502) - Common for PLCs
        nmap_command = f"nmap -p 502 -sV {ip_range}"
        process = subprocess.Popen(nmap_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        output = stdout.decode("utf-8")

        # Analyze nmap output for Schneider Electric TM221CE16R identification
        for line in output.splitlines():
            if "Schneider Electric" in line and "Modicon" in line: # Added "Modicon"
                # Extract the IP address from the nmap output
                parts = output.split("\n")
                for part in parts:
                    if "Nmap scan report for" in part:
                         plc_ip = part.split(" ")[4]
                         print(f"PLC IP Address found: {plc_ip}")
                         return plc_ip

        print("No Schneider Electric TM221CE16R PLC found with open port 502 in the specified range.")
        return None

    except FileNotFoundError:
        print("Error: nmap is not installed. Please install nmap to use IP address scanning.")
        return None
    except Exception as e:
        print(f"An error occurred during IP scanning: {e}")
        return None



# -------------------------------------------------------------------------
# PLC Program Upload Function
# -------------------------------------------------------------------------
def upload_plc_program(plc_ip, rack, slot, backup_file):
    """
    Connects to the PLC and uploads the program memory.

    Args:
        plc_ip (str): The IP address of the PLC.
        rack (int): The rack number of the PLC.
        slot (int): The slot number of the PLC.
        backup_file (str): The file to save the PLC program to.
    """
    try:
        client = snap7.client.Client()
        client.connect(plc_ip, rack, slot)
        print(f"Successfully connected to PLC at {plc_ip}:{rack}:{slot}")

        # Read the entire PLC memory (adjust size if needed based on your PLC's memory configuration)
        db_number = 1 # Usually, the main program resides in DB1
        start_address = 0
        size = 65535 # Maximum possible size, adjust based on PLC memory
        data = client.db_read(db_number, start_address, size)  #Read a data block from the PLC

        # Save the program data to a file
        with open(backup_file, "wb") as f:
            f.write(data)

        print(f"PLC program uploaded and saved to: {backup_file}")

    except snap7.exceptions.Snap7Exception as e:
        print(f"Snap7 Error during PLC communication: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if 'client' in locals() and client.get_connected():
            client.disconnect()
            print("Disconnected from PLC.")



# -------------------------------------------------------------------------
# Main Script Execution
# -------------------------------------------------------------------------
if __name__ == "__main__":
    plc_ip_address = find_plc_ip(PLC_IP_SCAN_RANGE)

    if plc_ip_address:
        upload_plc_program(plc_ip_address, PLC_RACK, PLC_SLOT, BACKUP_FILE)
    else:
        print("PLC IP address not found.  Exiting.")