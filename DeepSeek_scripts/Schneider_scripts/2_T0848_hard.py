import socket
import struct
import time
from scapy.all import ARP, Ether, srp

# Function to discover the PLC's IP address using ARP scanning
def discover_plc_ip(target_mac):
    # Create an ARP request packet
    arp = ARP(pdst="192.168.9.0/24")
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and receive the response
    result = srp(packet, timeout=2, verbose=0)[0]

    # Parse the response to find the PLC's IP address
    for sent, received in result:
        if received.hwsrc == target_mac:
            return received.psrc

    return None

# Function to send control messages to the PLC
def send_control_message(plc_ip, port=502):
    # Create a TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((plc_ip, port))

    # Example Modbus TCP message to manipulate the PLC's outputs
    # This is a simplified example and may need to be adjusted based on the PLC's configuration
    modbus_message = b"\x00\x01\x00\x00\x00\x06\x01\x05\x00\x00\xFF\x00"

    # Send the Modbus message
    sock.send(modbus_message)

    # Close the socket
    sock.close()

# Main script
if __name__ == "__main__":
    # Target PLC's MAC address (replace with the actual MAC address)
    plc_mac = "00:1D:9C:48:2A:3C"

    # Discover the PLC's IP address
    plc_ip = discover_plc_ip(plc_mac)

    if plc_ip:
        print(f"Found PLC at IP: {plc_ip}")
        
        # Send control messages to the PLC
        send_control_message(plc_ip)
        print("Control message sent to the PLC.")
    else:
        print("PLC not found on the network.")