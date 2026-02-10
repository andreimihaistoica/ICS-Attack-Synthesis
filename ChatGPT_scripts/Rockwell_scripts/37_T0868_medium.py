import logging
from scapy.all import ARP, Ether, srp
from pycomm3 import CIPDriver

# Configurations
SUBNET = "192.168.1.0/24"  # Change this to match your subnet
PLC_TAG_MODE = "Controller_Mode"  # This should point to the correct tag if different
DEBUG = True  # Set it to True to enable detailed logs

# Enable logging for debugging
logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def find_plc_ip(subnet):
    """
    Scans the local subnet to find an active Rockwell Automation Micro850 PLC.
    Uses ARP requests to detect live devices.
    """
    logging.info("[*] Scanning Network for Rockwell PLC...")
    ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=subnet), timeout=2, verbose=False)

    for sent, received in ans:
        ip = received.psrc
        mac = received.hwsrc

        # Rockwell OUI prefixes: 00-00-BC, 00-1D-9C, 00-0E-C6
        if mac.startswith(("00:00:BC", "00:1D:9C", "00:0E:C6")):
            logging.info(f"[+] Rockwell PLC Found: IP={ip}, MAC={mac}")
            return ip

    logging.warning("[!] No PLC found on the network.")
    return None


def get_plc_mode(plc_ip):
    """
    Connect to the PLC and retrieve its operating mode.
    """
    logging.info(f"[*] Connecting to PLC at {plc_ip}...")
    
    try:
        with CIPDriver(plc_ip) as plc:
            mode = plc.read(PLC_TAG_MODE)  # Read the mode tag from the PLC

            if mode is not None:
                mode_str = {
                    0: "PROGRAM",
                    1: "RUN",
                    2: "REMOTE RUN",
                    3: "STOP",
                    4: "RESET",
                    5: "TEST/MONITOR"
                }.get(mode.value, "UNKNOWN")

                logging.info(f"[+] PLC Operating Mode: {mode_str} (Raw: {mode.value})")
            else:
                logging.error("[!] Failed to retrieve PLC mode.")

    except Exception as e:
        logging.error(f"[!] Error connecting to PLC: {e}")


if __name__ == "__main__":
    # Step 1: Find the PLC's IP
    plc_ip = find_plc_ip(SUBNET)

    # Step 2: If PLC is found, retrieve its operating mode
    if plc_ip:
        get_plc_mode(plc_ip)
    else:
        logging.error("[!] Could not find a Rockwell PLC. Exiting.")