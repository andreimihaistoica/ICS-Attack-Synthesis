import socket
import struct
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException
from scapy.all import ARP, Ether, srp

# Function to discover the PLC's IP address
def discover_plc_ip(subnet):
    # Create an ARP request packet
    arp = ARP(pdst=subnet)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    # Send the packet and get the response
    result = srp(packet, timeout=2, verbose=False)[0]

    # Filter the response to find the PLC
    for sent, received in result:
        if received.psrc == "192.168.9.24":
            return received.psrc

    return None

# Function to read the I/O image from the PLC
def read_io_image(ip_address):
    try:
        # Connect to the PLC
        client = ModbusTcpClient(ip_address)
        client.connect()

        # Read digital inputs
        inputs = client.read_discrete_inputs(0, 9, unit=1)
        if inputs.isError():
            print("Error reading digital inputs")
            return

        # Read digital outputs
        outputs = client.read_coils(0, 7, unit=1)
        if outputs.isError():
            print("Error reading digital outputs")
            return

        # Print the I/O image
        print("Digital Inputs:")
        for i in range(9):
            print(f"Input %I0.{i}: {inputs.bits[i]}")

        print("\nDigital Outputs:")
        for i in range(7):
            print(f"Output %Q0.{i}: {outputs.bits[i]}")

    except ConnectionException as e:
        print(f"Connection error: {e}")
    finally:
        client.close()

# Main function
def main():
    # Define the subnet to scan
    subnet = "192.168.9.0/24"

    # Discover the PLC's IP address
    plc_ip = discover_plc_ip(subnet)
    if plc_ip:
        print(f"PLC found at IP address: {plc_ip}")
        # Read the I/O image from the PLC
        read_io_image(plc_ip)
    else:
        print("PLC not found on the network")

if __name__ == "__main__":
    main()