import snap7
import subprocess
import socket
import time

# Configuration
PLC_MODEL = "TM221CE16R"  # Adjust if needed
PLC_PORT = 102 # Standard S7 port.  Unlikely to need changing, but make it configurable
# You MAY need the TSAP for your TM221. Most of the time, it is fine to leave these default.
# But be aware, you can potentially knock a PLC offline if you hit it with the wrong TSAP.
TSAP_LOCAL = 0x0100  # Default TSAP Local
TSAP_REMOTE = 0x0200 # Default TSAP Remote


# Function to get the PLC's IP address. This relies on Nmap being installed and in your PATH.
# It scans the network and tries to identify the PLC based on its model.
def get_plc_ip():
    try:
        # Example Nmap command.  Adjust the subnet as needed.  A more specific subnet is FASTER.
        # -p 102 specifies port 102 (S7 protocol)
        # -Pn skips host discovery (assumes hosts are up)
        # --script s7-info attempts to identify S7 devices
        nmap_command = f"nmap -p {PLC_PORT} -Pn --script s7-info 192.168.1.0/24"  # <--- ADJUST SUBNET AS NEEDED!
        process = subprocess.Popen(nmap_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        output = stdout.decode()

        # Parse the Nmap output to find the PLC's IP address.  This is fragile, and may need adjustment
        # based on your network and Nmap output.
        for line in output.splitlines():
            if PLC_MODEL in line:  # Look for the PLC model in the output
                ip_address = line.split(" ")[0] #Assumes the IP address is the first element of the split line
                print(f"Found PLC at IP address: {ip_address}")
                return ip_address

        print(f"PLC with model {PLC_MODEL} not found on the network.  Check subnet and PLC status.")
        return None

    except FileNotFoundError:
        print("Error: Nmap not found. Please install Nmap and ensure it's in your system's PATH.")
        return None
    except Exception as e:
        print(f"An error occurred during IP address discovery: {e}")
        return None

# Function to restart the PLC using Snap7.
def restart_plc(ip_address):
    try:
        client = snap7.client.Client()

        # Connect to the PLC
        client.connect(ip_address, 0, 1)  # Rack 0, Slot 1 is typical for a TM221

        # Stop the PLC
        print("Stopping PLC...")
        client.plc_stop()
        time.sleep(5)  # Wait a few seconds for the PLC to stop. Adjust if needed.

        # Start the PLC.  Note: This will likely fail if the PLC is password protected.
        print("Starting PLC...")
        client.plc_start() #Throws an error when the device is password protected

        client.disconnect()  # Disconnect cleanly

        print("PLC restart command sent successfully.")

    except snap7.exceptions.Snap7Exception as e:
        print(f"Snap7 Error: {e}")
        if "ISO_TSAP" in str(e):
            print("Check that the TSAP settings are configured correctly.")
        if "Connect to PLC" in str(e):
            print("Check the PLC's IP address and network connectivity.")

    except Exception as e:
        print(f"An error occurred: {e}")


# Main script execution
if __name__ == "__main__":
    plc_ip = get_plc_ip()

    if plc_ip:
        restart_plc(plc_ip)
    else:
        print("Could not determine PLC IP address.  Exiting.")