import subprocess
import socket
import struct
import time
from scapy.all import ARP, Ether, srp
from pymodbus.client.sync import ModbusTcpClient

# Function to discover the PLC's IP address
def discover_plc_ip():
    # Get the local IP address
    local_ip = socket.gethostbyname(socket.gethostname())
    ip_prefix = '.'.join(local_ip.split('.')[:-1]) + '.'
    
    # Create an ARP request packet
    arp = ARP(pdst=ip_prefix + "0/24")
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    
    # Send the packet and capture the response
    result = srp(packet, timeout=2, verbose=False)[0]
    
    # Parse the response
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})
    
    # Filter out the PLC (assuming the PLC has a specific MAC address or IP range)
    plc_ip = None
    for device in devices:
        if device['mac'].startswith('00:11:22'):  # Example MAC address prefix for the PLC
            plc_ip = device['ip']
            break
    
    if plc_ip:
        print(f"PLC found at IP: {plc_ip}")
    else:
        print("PLC not found on the network.")
    
    return plc_ip

# Function to modify the PLC program
def modify_plc_program(plc_ip):
    # Connect to the PLC
    client = ModbusTcpClient(plc_ip)
    if not client.connect():
        print("Failed to connect to the PLC.")
        return
    
    print("Connected to the PLC.")
    
    # Example: Modify a specific register (for demonstration purposes)
    # This is a simple example. In a real scenario, you would need to know the specific registers and logic to modify.
    try:
        # Read the current value of a register
        response = client.read_holding_registers(address=0x00, count=1, unit=1)
        if response.isError():
            print("Error reading register.")
        else:
            print(f"Current value of register 0x00: {response.registers[0]}")
        
        # Modify the register value
        new_value = 12345  # Example new value
        client.write_register(address=0x00, value=new_value, unit=1)
        
        # Verify the modification
        response = client.read_holding_registers(address=0x00, count=1, unit=1)
        if response.isError():
            print("Error reading register after modification.")
        else:
            print(f"New value of register 0x00: {response.registers[0]}")
    
    except Exception as e:
        print(f"Error modifying PLC program: {e}")
    
    finally:
        client.close()
        print("Disconnected from the PLC.")

# Main function
def main():
    plc_ip = discover_plc_ip()
    if plc_ip:
        modify_plc_program(plc_ip)

if __name__ == "__main__":
    main()