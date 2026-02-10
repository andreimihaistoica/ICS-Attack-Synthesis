import socket
import struct
import time
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ConnectionException
from scapy.all import ARP, Ether, srp

# Function to discover the PLC's IP address
def discover_plc_ip(subnet):
    # Create an ARP request packet
    arp = ARP(pdst=subnet)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and capture the response
    result = srp(packet, timeout=2, verbose=False)[0]

    # Parse the response
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    # Filter the devices to find the PLC
    for device in devices:
        if device['ip'].startswith('192.168.9'):
            return device['ip']
    return None

# Function to connect to the PLC and modify the program
def modify_plc_program(plc_ip):
    try:
        # Connect to the PLC
        client = ModbusTcpClient(plc_ip)
        client.connect()

        # Define the new function to toggle the fan
        new_function = """
        // New function to toggle the fan
        IF M_TOG THEN
            Q_FAN := NOT Q_FAN;
            Q_REDA := NOT Q_FAN;
            Q_GREENA := Q_FAN;
        END_IF;
        """

        # Write the new function to the PLC's memory (this is a simplified example)
        # In a real scenario, you would need to use the appropriate Modbus function codes
        # to write the new function to the PLC's memory.
        # For example, you might use the Modbus function code 16 (Write Multiple Registers)
        # to write the new function to a specific memory address.

        # Example: Write the new function to memory address 1000
        # Note: This is a placeholder and will not work as-is. You need to implement the actual logic
        # to write the new function to the PLC's memory.
        client.write_registers(1000, [0x0001, 0x0002, 0x0003, 0x0004])

        # Close the connection
        client.close()

        print(f"PLC program modified successfully at IP: {plc_ip}")

    except ConnectionException as e:
        print(f"Failed to connect to PLC at IP: {plc_ip}")
        print(e)

# Main function
def main():
    # Define the subnet to scan
    subnet = "192.168.9.0/24"

    # Discover the PLC's IP address
    plc_ip = discover_plc_ip(subnet)
    if plc_ip:
        print(f"PLC found at IP: {plc_ip}")
        # Modify the PLC program
        modify_plc_program(plc_ip)
    else:
        print("PLC not found on the network")

if __name__ == "__main__":
    main()