import socket
from scapy.all import ARP, Ether, srp

# Function to discover the PLC's IP address using ARP scan
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

# Function to detect the PLC's operating mode via Modbus TCP/IP
def detect_operating_mode(plc_ip):
    # Create a socket connection to the PLC
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((plc_ip, 502))  # Modbus TCP port is 502
    except Exception as e:
        print(f"Failed to connect to PLC: {e}")
        return None

    # Modbus request to read the operating mode (assuming register address 0x0001)
    modbus_request = b'\x00\x01\x00\x00\x00\x06\x01\x03\x00\x01\x00\x01'

    try:
        s.send(modbus_request)
        response = s.recv(1024)
    except Exception as e:
        print(f"Failed to communicate with PLC: {e}")
        return None
    finally:
        s.close()

    # Parse the response to determine the operating mode
    if len(response) >= 9:
        mode = int.from_bytes(response[9:10], byteorder='big')
        return mode
    else:
        return None

# Main function
if __name__ == "__main__":
    # Replace with the MAC address of the PLC
    plc_mac = "00:1D:9C:C7:B0:50"

    # Discover the PLC's IP address
    plc_ip = discover_plc_ip(plc_mac)
    if plc_ip:
        print(f"Found PLC at IP: {plc_ip}")

        # Detect the operating mode
        mode = detect_operating_mode(plc_ip)
        if mode is not None:
            modes = {
                0: "Program",
                1: "Run",
                2: "Remote",
                3: "Stop",
                4: "Reset",
                5: "Test/Monitor"
            }
            print(f"PLC Operating Mode: {modes.get(mode, 'Unknown')}")
        else:
            print("Failed to detect operating mode.")
    else:
        print("PLC not found on the network.")