import socket
import time
from opcua import Client
from scapy.all import ARP, Ether, srp

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Define the target IP range to scan (e.g., 192.168.1.0/24)
    target_ip = "192.168.1.0/24"
    
    # Create an ARP request packet
    arp = ARP(pdst=target_ip)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    
    # Send the packet and capture the response
    result = srp(packet, timeout=2, verbose=False)[0]
    
    # Parse the response to find the PLC's IP address
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})
    
    # Filter the devices to find the PLC (assuming the PLC has a specific MAC address or name)
    plc_ip = None
    for device in devices:
        # Example: Assuming the PLC has a specific MAC address
        if device['mac'] == "00:11:22:33:44:55":
            plc_ip = device['ip']
            break
    
    if plc_ip:
        print(f"PLC found at IP: {plc_ip}")
    else:
        print("PLC not found in the network.")
    
    return plc_ip

# Function to connect to the PLC and collect information
def collect_plc_info(plc_ip):
    if not plc_ip:
        print("PLC IP address not found. Aborting.")
        return
    
    # Create an OPC UA client
    client = Client(f"opc.tcp://{plc_ip}:4840")
    
    try:
        # Connect to the PLC
        client.connect()
        print(f"Connected to PLC at {plc_ip}")
        
        # Enumerate and collect information
        root = client.get_root_node()
        objects = client.get_objects_node()
        
        # Example: List all objects and their properties
        for obj in objects.get_children():
            print(f"Object: {obj.get_browse_name()}")
            for var in obj.get_children():
                print(f"  Variable: {var.get_browse_name()} - Value: {var.get_value()}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Disconnect from the PLC
        client.disconnect()
        print("Disconnected from PLC")

# Main function
def main():
    plc_ip = discover_plc_ip()
    collect_plc_info(plc_ip)

if __name__ == "__main__":
    main()