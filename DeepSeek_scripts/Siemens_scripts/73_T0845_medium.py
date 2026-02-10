from snap7 import client
from scapy.all import ARP, Ether, srp
import sys

def find_plc_ip(target_mac):
    # Create an ARP request packet
    arp = ARP(pdst="192.168.1.0/24")  # Adjust the network range as needed
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and receive the response
    result = srp(packet, timeout=2, verbose=0)[0]

    # Parse the response to find the PLC's IP address
    for sent, received in result:
        if received.hwsrc.lower() == target_mac.lower():
            return received.psrc

    return None

def upload_program(plc_ip):
    # Create a Snap7 client
    plc = client.Client()

    try:
        # Connect to the PLC
        plc.connect(plc_ip, 0, 1)

        # Upload the program from the PLC
        program_data = plc.upload()

        # Save the program to a file
        with open("plc_program.hex", "wb") as f:
            f.write(program_data)

        print(f"Program successfully uploaded and saved as 'plc_program.hex'")

    except Exception as e:
        print(f"Failed to upload program: {e}")

    finally:
        # Disconnect from the PLC
        plc.disconnect()

if __name__ == "__main__":
    # Replace with the MAC address of your Siemens S7-1200 PLC
    plc_mac = "00:1C:06:XX:XX:XX"  # Replace XX:XX:XX with your PLC's MAC address

    # Step 1: Find the PLC's IP address
    plc_ip = find_plc_ip(plc_mac)

    if plc_ip:
        print(f"Found PLC at IP address: {plc_ip}")

        # Step 2: Upload the program from the PLC
        upload_program(plc_ip)
    else:
        print("Could not find the PLC on the network. Check the MAC address and network settings.")