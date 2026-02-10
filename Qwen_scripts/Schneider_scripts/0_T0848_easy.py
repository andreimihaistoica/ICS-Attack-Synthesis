import socket
import struct
from scapy.all import ARP, Ether, srp
from pymodbus.client.sync import ModbusTcpClient

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the target IP range to scan
    ip_range = "192.168.1.0/24"  # Change this to your network range

    # Create an ARP request packet
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and capture the response
    result = srp(packet, timeout=2, verbose=False)[0]

    # Parse the response to find the PLC
    for sent, received in result:
        print(f"IP: {received.psrc} - MAC: {received.hwsrc}")
        # Add logic to identify the PLC based on MAC address or other criteria
        # For example, if you know the PLC's MAC address:
        if received.hwsrc == "00:11:22:33:44:55":  # Replace with the actual PLC MAC address
            return received.psrc

    return None

# Function to send a command to the PLC
def send_command_to_plc(plc_ip, command):
    # Create a Modbus TCP client
    client = ModbusTcpClient(plc_ip)

    # Connect to the PLC
    if client.connect():
        print(f"Connected to PLC at {plc_ip}")

        # Send a command (example: write a value to a register)
        # Replace the register address and value as needed
        register_address = 0x0001
        value = 1
        result = client.write_register(register_address, value)

        if result.isError():
            print("Failed to send command to PLC")
        else:
            print("Command sent successfully to PLC")

        # Close the connection
        client.close()
    else:
        print(f"Failed to connect to PLC at {plc_ip}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        print(f"PLC found at IP: {plc_ip}")
        # Send a command to the PLC
        send_command_to_plc(plc_ip, command=1)
    else:
        print("PLC not found")

if __name__ == "__main__":
    main()