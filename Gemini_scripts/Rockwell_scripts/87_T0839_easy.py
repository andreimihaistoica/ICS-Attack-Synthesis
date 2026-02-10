import socket
import struct
import subprocess
import os
import time
import random
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration ---
#  Remember, this is a SIMULATION.  Replacing firmware in reality is VERY risky.
#  This script simulates the steps an attacker *might* take.
SIMULATE_FIRMWARE_REFLASH = True  # Set to False to skip the simulated firmware reflash
TARGET_VENDOR = "GenericPLC" #change depending on PLC Model
TARGET_MODEL = "XYZ-123" #change depending on PLC Model
MALICIOUS_FIRMWARE_FILENAME = "malicious_ethernet_firmware.bin"  # FAKE firmware file
FAKE_FIRMWARE_REFLASH_TIME = 10  # Seconds to simulate firmware reflash
DELAYED_ATTACK_TIME = 60 #seconds
FIELD_DEVICE_WORM_TARGET_COUNT = 5 # How many devices to infect in the worm simulation
RANDOM_ATTACK_PROBABILITY = 0.1  # Probability of random attack on each run (10%)

# Network Settings (Used for worm simulation and PLC discovery)
NETWORK_INTERFACE = "eth0"  # Change if your network interface is different

# --- Helper Functions ---

def find_plc_ip_address():
    """
    Attempts to discover the PLC's IP address by sniffing network traffic.
    This is a simplified simulation; real discovery would be more complex.

    Returns:
        str: The PLC's IP address, or None if not found.
    """
    logging.info("Attempting to discover PLC IP address...")

    try:
        #Use a simple ping sweep to find the PLC
        ip_prefix = ".".join(get_own_ip_address().split(".")[:3]) + "."
        for i in range(1, 255):
            target_ip = ip_prefix + str(i)
            result = subprocess.run(['ping', '-c', '1', '-W', '1', target_ip], capture_output=True, text=True)
            if result.returncode == 0 and "ttl=" in result.stdout.lower():
                logging.info(f"Possible PLC IP found: {target_ip}")
                #check to confirm it is the TARGET_VENDOR and TARGET_MODEL by sending a connection request
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                try:
                    sock.connect((target_ip, 502))
                    sock.sendall(b"\x00\x01\x00\x00\x00\x06\x01\x03\x00\x00\x00\x01")
                    response = sock.recv(1024)
                    sock.close()
                    if response:
                        # Vendor and model identification logic here.
                        # This is a placeholder as real vendor/model detection is protocol-specific
                        if TARGET_VENDOR in str(response) and TARGET_MODEL in str(response):
                            logging.info(f"Confirmed PLC IP: {target_ip}")
                            return target_ip
                except (socket.error, socket.timeout):
                    sock.close()
                    pass  # Ignore connection errors and timeouts


        logging.warning("PLC IP address discovery failed.")
        return None
    except Exception as e:
        logging.error(f"Error during PLC IP discovery: {e}")
        return None

def get_own_ip_address():
    """
    Gets the IP address of the interface used to communicate with the PLC.

    Returns:
        str: The IP address of the specified network interface.
             Returns None if the interface is not found or has no IP address.
    """
    try:
        # Use 'ip addr show' to get interface information
        result = subprocess.run(['ip', 'addr', 'show', NETWORK_INTERFACE], capture_output=True, text=True, check=True)
        output = result.stdout

        # Regular expression to find the IP address in the output
        ip_match = re.search(r'inet\s+([\d.]+)', output)

        if ip_match:
            return ip_match.group(1)
        else:
            logging.error(f"No IP address found for interface {NETWORK_INTERFACE}")
            return None

    except subprocess.CalledProcessError as e:
        logging.error(f"Error getting IP address: {e}")
        return None
    except FileNotFoundError:
        logging.error("The 'ip' command was not found.  Ensure it is in your system's PATH.")
        return None

def simulate_ethernet_card_compromise():
    """Simulates the attacker gaining control of the Ethernet card."""
    logging.info("Simulating Ethernet card compromise...")
    # In a real attack, this would involve exploiting a vulnerability
    # to gain root access on the embedded system.
    logging.info("Compromise successful (simulated).")

def simulate_firmware_reflash(filename):
    """Simulates flashing malicious firmware to the Ethernet card."""
    logging.info(f"Simulating flashing malicious firmware: {filename}")
    if not SIMULATE_FIRMWARE_REFLASH:
        logging.warning("Firmware reflash simulation skipped (SIMULATE_FIRMWARE_REFLASH = False)")
        return

    if not os.path.exists(filename):
        logging.error(f"Firmware file not found: {filename}")
        return

    logging.info(f"Erasing existing firmware (simulated)...")
    time.sleep(2)
    logging.info(f"Writing new firmware (simulated)...")
    time.sleep(FAKE_FIRMWARE_REFLASH_TIME)
    logging.info("Firmware reflash complete (simulated).")

def delayed_attack(plc_ip):
    """Simulates a delayed attack against the PLC."""
    logging.info(f"Preparing delayed attack.  Will launch in {DELAYED_ATTACK_TIME} seconds...")
    time.sleep(DELAYED_ATTACK_TIME)
    logging.info("Launching delayed attack (simulated).")
    # Replace this with the actual attack code.  This is just a placeholder.
    # Example:  stop_plc(plc_ip)  or manipulate_process_variable(plc_ip, "TankLevel", 95)
    logging.warning("Delayed attack simulation:  No actual attack implemented!")

def brick_ethernet_card():
    """Simulates bricking the Ethernet card by writing bad data to flash."""
    logging.warning("Simulating bricking of Ethernet card...")
    # This is a *destructive* simulation.  Be careful.
    # In reality, this would involve carefully crafting data to
    # corrupt the firmware in a way that prevents booting.
    logging.warning("Ethernet card is now unusable (simulated).")

def random_attack_or_failure():
    """Simulates a random attack or failure."""
    logging.info("Executing random attack/failure (simulated).")
    if random.random() < 0.5:  # 50% chance of attack
        logging.warning("Random attack triggered (simulated).")
        # Replace with your attack code here
        logging.warning("No random attack implemented!")
    else:
        logging.warning("Random failure triggered (simulated).")
        brick_ethernet_card()

def find_and_compromise_field_devices():
    """Simulates a worm spreading to other field devices of the same model."""
    logging.info("Searching for other vulnerable field devices (simulated worm)...")
    # This is a highly simplified simulation.  Real worm propagation would be much more complex.

    # Simulate network scanning
    network_prefix = ".".join(get_own_ip_address().split(".")[:3]) + "."
    compromised_count = 0
    for i in range(2, 255): # Avoid .1 (likely gateway) and .0
        target_ip = network_prefix + str(i)
        if target_ip == get_own_ip_address() or compromised_count >= FIELD_DEVICE_WORM_TARGET_COUNT:
            continue

        logging.info(f"Probing {target_ip}...")
        # Simulate checking if the device is vulnerable (same model, vulnerable firmware)
        if random.random() < 0.3: # Simulate 30% chance of vulnerability.
            logging.warning(f"Vulnerable device found at {target_ip}! Compromising...")
            compromised_count += 1
            # Simulate the worm spreading by reflashing the firmware.
            simulate_firmware_reflash(MALICIOUS_FIRMWARE_FILENAME)
        else:
            logging.info(f"{target_ip} is not vulnerable or not the right model.")
    logging.info(f"Worm simulation complete. Compromised {compromised_count} devices.")

def attack_other_cards_on_field_device():
    """Simulates using the compromised Ethernet card to attack other modules."""
    logging.info("Simulating attack on other modules via the Ethernet card...")
    # Replace this with the actual attack on other modules. This is just a placeholder.
    logging.warning("No attack on other modules implemented!")

# --- Main Script ---

def main():
    """Main function to orchestrate the simulated attack."""

    plc_ip = find_plc_ip_address()
    if not plc_ip:
        logging.error("Failed to find PLC IP address. Exiting.")
        return

    logging.info("Starting attack simulation...")

    # 1. Compromise the Ethernet card.
    simulate_ethernet_card_compromise()

    # 2. Flash malicious firmware.
    simulate_firmware_reflash(MALICIOUS_FIRMWARE_FILENAME)

    # 3. Execute chosen attack(s).  Choose ONE or more of the following:

    # a) Delayed attack:
    #delayed_attack(plc_ip)

    # b) Brick the Ethernet card:
    #brick_ethernet_card()

    # c) Random Attack or Failure:
    #if random.random() < RANDOM_ATTACK_PROBABILITY:
    #    random_attack_or_failure()

    # d) Field Device Worm:
    #find_and_compromise_field_devices()

    # e) Attack other cards on the field device:
    #attack_other_cards_on_field_device()

    logging.info("Attack simulation complete.")


if __name__ == "__main__":
    main()