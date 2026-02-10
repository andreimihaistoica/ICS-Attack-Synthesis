import snap7
from scapy.all import ARP, Ether, srp
import sys

def find_plc_ip(network_prefix):
    # Create an ARP request packet
    arp = ARP(pdst=f"{network_prefix}.0/24")
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and receive the response
    result = srp(packet, timeout=2, verbose=0)[0]

    # Parse the response to find the PLC's IP address
    plc_ip = None
    for sent, received in result:
        if received.hwsrc.startswith("00:1c:06"):  # Example MAC prefix for Siemens PLCs
            plc_ip = received.psrc
            print(f"Found PLC at IP: {plc_ip}")
            break

    return plc_ip

def upload_program(plc_ip, rack=0, slot=1):
    # Create a snap7 client and connect to the PLC
    client = snap7.client.Client()
    client.connect(plc_ip, rack, slot)

    if client.get_connected():
        print("Connected to PLC.")

        # Upload the program from the PLC
        try:
            program_data = client.upload()
            with open("plc_program.hex", "wb") as f:
                f.write(program_data)
            print("Program uploaded and saved as 'plc_program.hex'.")
        except Exception as e:
            print(f"Failed to upload program: {e}")
    else:
        print("Failed to connect to PLC.")

    client.disconnect()

if __name__ == "__main__":
    # Define the network prefix (e.g., "192.168.1")
    network_prefix = "192.168.1"

    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip(network_prefix)

    if plc_ip:
        # Step 2: Upload the program from the PLC
        upload_program(plc_ip)
    else:
        print("PLC not found on the network.")