import socket
import struct
from scapy.all import ARP, Ether, srp

# Function to discover the PLC's IP address on the network
def discover_plc_ip(target_mac):
    # Create an ARP request packet
    arp = ARP(pdst="192.168.1.0/24")  # Adjust the network range as needed
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    # Send the packet and receive the response
    result = srp(packet, timeout=2, verbose=0)[0]

    # Parse the response to find the PLC's IP address
    for sent, received in result:
        if received.hwsrc.lower() == target_mac.lower():
            return received.psrc

    return None

# Function to change the PLC's operating mode
def change_plc_mode(plc_ip, mode):
    # Example: Simulate sending a command to change the PLC mode
    # Replace this with actual API calls or protocol-specific commands
    try:
        # Create a socket connection to the PLC
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((plc_ip, 502))  # Default Modbus TCP port
            print(f"Connected to PLC at {plc_ip}")

            # Example command to change mode (replace with actual protocol-specific command)
            if mode == "Program":
                command = b"\x00\x01\x00\x00\x00\x06\x01\x06\x00\x64\x00\x01"  # Example Modbus command
            elif mode == "Run":
                command = b"\x00\x01\x00\x00\x00\x06\x01\x06\x00\x64\x00\x02"  # Example Modbus command
            else:
                print(f"Unsupported mode: {mode}")
                return

            # Send the command
            s.sendall(command)
            print(f"Sent command to change PLC mode to {mode}")

            # Receive the response
            response = s.recv(1024)
            print(f"Received response: {response}")

    except Exception as e:
        print(f"Error changing PLC mode: {e}")

# Main script
if __name__ == "__main__":
    # PLC's MAC address (replace with the actual MAC address of the PLC)
    plc_mac = "00:1D:9C:C7:B0:70"  # Example MAC address

    # Discover the PLC's IP address
    plc_ip = discover_plc_ip(plc_mac)
    if plc_ip:
        print(f"Discovered PLC IP address: {plc_ip}")

        # Change the PLC's operating mode to "Program"
        change_plc_mode(plc_ip, "Program")
    else:
        print("PLC not found on the network.")