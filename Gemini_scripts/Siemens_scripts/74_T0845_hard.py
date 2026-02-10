import snap7
import struct
import os
import subprocess

# Configuration
PLC_IP = None  # Initially unknown, will be discovered
PLC_RACK = 0
PLC_SLOT = 1
DB_NUMBER = None  #Not relevant for program upload, keep it as None
OUTPUT_FILE = "plc_program_upload.awl"  # File to save the uploaded program

#Siemens S7 API client
client = snap7.client.Client()

def find_plc_ip():
    """
    Attempts to discover the PLC's IP address by scanning the network using nmap.
    Requires nmap to be installed and accessible in the system's PATH.
    """
    try:
        # Run nmap to discover Siemens PLCs (using a fingerprint)
        nmap_command = ["nmap", "-p102", "-T4", "-F", "192.168.0.0/24"] # Use 192.168.0.0/24 - Change if necessary
        result = subprocess.run(nmap_command, capture_output=True, text=True, check=True) #check=True raises exception if nmap fails

        # Parse nmap output for IP addresses with Siemens S7 service
        for line in result.stdout.splitlines():
            if "Siemens S7" in line:
                PLC_IP = line.split()[4]  # Extract the IP address
                print(f"PLC IP address discovered: {PLC_IP}")
                return PLC_IP #return the ip, so it can be used in the main flow
        print("No Siemens S7 PLC found on the network using nmap.  Make sure nmap is installed and the network range is correct.")
        return None  # PLC not found

    except FileNotFoundError:
        print("Error: nmap is not installed or not in your system's PATH.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error running nmap: {e}")
        return None

def upload_program(ip_address, output_file):
    """
    Uploads the entire PLC program as AWL source code.

    Args:
        ip_address (str): The IP address of the PLC.
        output_file (str): The name of the file to save the AWL source code.
    """
    try:
        client.connect(ip_address, PLC_RACK, PLC_SLOT)

        # Retrieve the entire program as AWL source code
        # This is accomplished using the AG_EXPORT system function.
        # AG_EXPORT is technically undocumented, but widely known and used
        # for program backup and recovery.  It returns the entire program
        # as an AWL (STL) source file.

        # The 'SYSTEM' keyword in the function specifies that the function
        # should operate in the 'System' context (the operating system of the PLC).
        # AG_EXPORT is a function to extract a project, not just blocks.

        # This relies on a function within Snap7 that directly calls the AG_EXPORT SFB.

        awl_data = client.ag_read_program()

        # Save the AWL data to a file
        with open(output_file, "wb") as f:  # Open in binary write mode
            f.write(awl_data)

        print(f"PLC program uploaded successfully and saved to {output_file}")

    except Exception as e:
        print(f"Error uploading PLC program: {e}")
    finally:
        if client.get_connected():
            client.disconnect()

if __name__ == "__main__":
    # Discover PLC IP Address
    PLC_IP = find_plc_ip() # set plc_ip

    if PLC_IP:
        # Upload the PLC program
        upload_program(PLC_IP, OUTPUT_FILE)
    else:
        print("Could not discover PLC IP address.  Exiting.")