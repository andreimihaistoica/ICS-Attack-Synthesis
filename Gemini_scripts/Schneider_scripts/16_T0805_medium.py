import socket
import time
import subprocess
import re

def find_plc_ip():
    """
    Attempts to discover the PLC's IP address on the network.
    This function assumes that the PLC is reachable via a standard network discovery tool like 'arp'.
    Adjust the method if 'arp' is not suitable for your specific network configuration.

    Returns:
        str: The IP address of the PLC if found, otherwise None.
    """
    try:
        # Execute 'arp -a' command to get ARP table.  Adjust as needed.
        arp_process = subprocess.Popen(['arp', '-a'], stdout=subprocess.PIPE)
        arp_output, _ = arp_process.communicate()
        arp_output = arp_output.decode('utf-8')

        # Iterate through the ARP entries and look for the PLC's MAC address.
        # **IMPORTANT:**  Replace 'YOUR_PLC_MAC_ADDRESS' with the actual MAC address of your TM221CE16R PLC.
        #  You MUST know your PLC's MAC address for this discovery method to work.
        plc_mac_address = 'YOUR_PLC_MAC_ADDRESS'  # <--- REPLACE WITH ACTUAL MAC ADDRESS.  Format e.g., 00:11:22:33:44:55

        for line in arp_output.splitlines():
            if plc_mac_address.lower() in line.lower():  # Case-insensitive match
                match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', line)  # Extract IP address
                if match:
                    return match.group(1)
        return None #PLC mac was not found
    except Exception as e:
        print(f"Error finding PLC IP: {e}")
        return None


def block_serial_com(plc_ip, com_port):
    """
    Blocks a serial COM port by opening and holding a TCP connection.

    Args:
        plc_ip (str): The IP address of the PLC (or serial-to-Ethernet converter).
        com_port (int): The serial COM port number to block (1, 2, 3, etc.).
    """
    port = 20000 + com_port  # Assuming ports 20001, 20002, 20003 correspond to COM1, COM2, COM3, respectively

    try:
        # Create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the PLC's serial-to-Ethernet converter
        s.connect((plc_ip, port))
        print(f"Successfully connected to {plc_ip}:{port}. Holding the connection open...")

        # Keep the connection open indefinitely (or until manually terminated)
        while True:
            time.sleep(60)  # Sleep for 60 seconds to avoid excessive CPU usage

    except socket.error as e:
        print(f"Socket error: {e}")
    except KeyboardInterrupt:
        print("Interrupted. Closing the connection...")
    finally:
        if 's' in locals(): # Check if s is defined
            s.close()
            print("Connection closed.")


if __name__ == "__main__":
    plc_ip = find_plc_ip()

    if plc_ip:
        print(f"PLC IP address found: {plc_ip}")
        com_port_to_block = 1  # Change this to the COM port you want to block (e.g., 2 or 3)
        print(f"Blocking COM port {com_port_to_block} by holding open a TCP connection...")
        block_serial_com(plc_ip, com_port_to_block)
    else:
        print("Could not automatically determine PLC IP address.  Please ensure PLC MAC address is correct and arp is working. Exiting")