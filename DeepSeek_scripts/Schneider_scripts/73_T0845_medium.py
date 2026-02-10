from scapy.all import ARP, Ether, srp
from pymodbus.client.sync import ModbusTcpClient
import os

def find_plc_ip(target_mac):
    # Create an ARP request packet
    arp = ARP(pdst="192.168.1.0/24")  # Adjust the subnet as needed
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
    # Connect to the PLC using Modbus TCP
    client = ModbusTcpClient(plc_ip)
    if not client.connect():
        print(f"Failed to connect to PLC at {plc_ip}")
        return

    try:
        # Example: Read the program from the PLC
        # Adjust the function code and address as per your PLC's configuration
        response = client.read_holding_registers(address=0, count=10, unit=1)
        if response.isError():
            print("Error reading from PLC")
        else:
            print("Program data read from PLC:", response.registers)

            # Save the program to a file
            with open("plc_program.txt", "w") as file:
                file.write(str(response.registers))
            print("Program saved to plc_program.txt")

    finally:
        client.close()

if __name__ == "__main__":
    # Replace with the MAC address of your PLC
    plc_mac = "00:1D:9C:C7:B0:01"  # Example MAC address

    # Find the PLC's IP address
    plc_ip = find_plc_ip(plc_mac)
    if plc_ip:
        print(f"Found PLC at IP: {plc_ip}")

        # Upload the program from the PLC
        upload_program(plc_ip)
    else:
        print("PLC not found on the network.")