import logging
import time
from pycomm3 import CIPDriver
from scapy.all import ARP, Ether, srp

# Configure logging
logging.basicConfig(level=logging.INFO)

# Define network range for PLC discovery
NETWORK_RANGE = "192.168.1.0/24"

def discover_plc():
    """
    Performs ARP scan to find the Rockwell PLC on local network.
    Returns the detected IP address.
    """
    logging.info("Scanning network to find Rockwell Micro850 PLC...")

    # Create ARP request
    arp_request = ARP(pdst=NETWORK_RANGE)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp_request

    # Send ARP request and get responses
    result = srp(packet, timeout=2, verbose=False)[0]

    # Check active devices
    for sent, received in result:
        if "Rockwell" in received.summary():
            logging.info(f"Found Rockwell PLC at {received.psrc}")
            return received.psrc

    logging.error("No Rockwell PLC found on the network!")
    return None

def activate_firmware_update_mode(plc_ip):
    """
    Connects to the PLC via CIP and attempts to activate firmware update mode.
    """
    logging.info(f"Attempting to activate firmware update mode on {plc_ip}...")

    try:
        # Connect to PLC
        with CIPDriver(f"ethernet/ip/{plc_ip}") as plc:
            # Service Code 0x4F for Firmware Update Activation (Example)
            SERVICE_CODE = 0x4F  
            CLASS_ID = 0x67  # CIP class related to firmware handling
            INSTANCE_ID = 1  
            ATTRIBUTE_ID = 1

            # Send request
            response = plc.generic_message(
                service=SERVICE_CODE,
                class_code=CLASS_ID,
                instance=INSTANCE_ID,
                attribute=ATTRIBUTE_ID,
                connected=False,
            )

            if response:
                logging.info("Firmware update mode activated successfully.")
            else:
                logging.error("Failed to activate firmware update mode.")

    except Exception as e:
        logging.error(f"Error communicating with PLC: {e}")

def main():
    plc_ip = discover_plc()
    if plc_ip:
        activate_firmware_update_mode(plc_ip)
    else:
        logging.error("PLC not found. Exiting.")

if __name__ == "__main__":
    main()