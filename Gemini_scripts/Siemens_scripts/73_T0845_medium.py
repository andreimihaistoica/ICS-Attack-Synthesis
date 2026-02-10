import snap7
import snap7.util
import os
import subprocess
import socket
import struct
import re

# Configuration - Change these values as needed
PLC_RACK = 0
PLC_SLOT = 1
OUTPUT_DIRECTORY = "PLC_Backups"
VMWARE_NSLOOKUP_PATH = r"C:\Program Files (x86)\VMware\VMware Workstation\nslookup.exe"  # Example path, adjust if different

def find_plc_ip_address_vmware():
    """
    Attempts to find the PLC IP address by scanning the ARP table.
    This version leverages VMware's nslookup.exe if available.
    Returns:
        string: The IP address of the PLC if found, None otherwise.
    """
    try:
        # Use VMware's nslookup to get the MAC address resolution
        command = [VMWARE_NSLOOKUP_PATH, "-d", "-t", "A", "_gateway"]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        output = result.stdout
        # Regular expression to extract the IP address from the output.
        ip_regex = r"IP Address = (.*?)\n"
        ip_matches = re.findall(ip_regex, output)
        if ip_matches:
            # Use the first discovered IP address.
            plc_ip_address = ip_matches[0]
            print(f"Found potential PLC IP address: {plc_ip_address}")
            return plc_ip_address
        else:
            print("PLC IP address not found in ARP table using VMware's nslookup.")
            return None
    except FileNotFoundError:
        print("VMware's nslookup.exe not found.  Make sure it is installed and the path is set correctly.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error executing nslookup: {e}")
        return None


def upload_plc_program(plc_ip_address, rack, slot, output_directory):
    """
    Uploads the PLC program using snap7.

    Args:
        plc_ip_address (str): The IP address of the PLC.
        rack (int): The PLC rack number.
        slot (int): The PLC slot number.
        output_directory (str): The directory to save the PLC program to.
    """
    try:
        client = snap7.client.Client()
        client.connect(plc_ip_address, rack, slot)

        print(f"Connected to PLC at {plc_ip_address}, Rack: {rack}, Slot: {slot}")

        # Create the output directory if it doesn't exist
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # Get the PLC program
        print("Retrieving PLC program...")
        plc_program = client.download()

        # Get PLC information (optional but useful for filename)
        plc_info = client.get_cpu_info()
        cpu_name = plc_info.ModuleTypeName.replace(" ", "_") #Clean up spaces

        # Save the PLC program to a file
        output_filename = os.path.join(output_directory, f"{cpu_name}_{plc_ip_address.replace('.', '_')}_program.s7p")
        with open(output_filename, "wb") as f:
            f.write(plc_program)

        print(f"PLC program saved to: {output_filename}")

        client.disconnect()
        print("Disconnected from PLC.")

    except snap7.exceptions.Snap7Exception as e:
        print(f"Error during PLC communication: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    """
    Main function to find the PLC IP and upload the program.
    """
    plc_ip_address = find_plc_ip_address_vmware()

    if plc_ip_address:
        upload_plc_program(plc_ip_address, PLC_RACK, PLC_SLOT, OUTPUT_DIRECTORY)
    else:
        print("PLC IP address not found.  Unable to upload program.")

if __name__ == "__main__":
    main()