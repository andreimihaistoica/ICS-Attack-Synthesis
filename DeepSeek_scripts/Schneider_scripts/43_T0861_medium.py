import socket
from scapy.all import ARP, Ether, srp

# Function to find the PLC's IP address
def find_plc_ip():
    print("Scanning network for the PLC...")
    arp = ARP(pdst="192.168.1.1/24")  # Adjust the subnet to match your network
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp
    result = srp(packet, timeout=2, verbose=0)[0]

    for sent, received in result:
        if "Schneider Electric" in received.hwsrc:  # Check if the MAC address belongs to Schneider Electric
            print(f"PLC found at IP: {received.psrc}")
            return received.psrc

    print("PLC not found on the network.")
    return None

# Function to collect point and tag values from the PLC
def collect_tags(plc_ip):
    try:
        # Establish a connection to the PLC (replace with the correct protocol and port)
        plc_port = 502  # Modbus TCP port (default)
        plc_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        plc_socket.connect((plc_ip, plc_port))
        print(f"Connected to PLC at {plc_ip}")

        # Example: Send a Modbus request to read holding registers (adjust as needed)
        request = b"\x00\x01\x00\x00\x00\x06\x01\x03\x00\x00\x00\x0A"  # Read 10 registers starting from address 0
        plc_socket.send(request)
        response = plc_socket.recv(1024)

        # Parse the response (example for Modbus TCP)
        if len(response) > 0:
            print("Received data from PLC:")
            print(response.hex())
            # Extract and print tag values (this is just an example; adjust based on your PLC's protocol)
            for i in range(0, len(response), 2):
                value = int.from_bytes(response[i:i+2], byteorder='big')
                print(f"Tag {i//2}: {value}")
        else:
            print("No response received from the PLC.")

    except Exception as e:
        print(f"Error communicating with PLC: {e}")
    finally:
        plc_socket.close()

# Main script
if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        collect_tags(plc_ip)
    else:
        print("Cannot proceed without the PLC's IP address.")