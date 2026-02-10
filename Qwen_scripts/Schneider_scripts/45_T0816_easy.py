import subprocess
import socket
import time
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
    result = srp(packet, timeout=3, verbose=0)[0]
    
    # Parse the response to find the PLC's IP address
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})
    
    # Filter the devices to find the PLC (you may need to adjust this based on your environment)
    plc_ip = None
    for device in devices:
        try:
            # Example: Check if the device is a PLC by its MAC address or other criteria
            if device['mac'].startswith("00:11:22"):  # Replace with the actual MAC address or criteria
                plc_ip = device['ip']
                break
        except Exception as e:
            print(f"Error: {e}")
    
    if plc_ip:
        print(f"PLC found at IP: {plc_ip}")
    else:
        print("PLC not found.")
    
    return plc_ip

# Function to send a restart/shutdown command to the PLC
def restart_plc(plc_ip):
    try:
        # Create a Modbus TCP client
        client = ModbusTcpClient(plc_ip)
        
        # Connect to the PLC
        if client.connect():
            print(f"Connected to PLC at {plc_ip}")
            
            # Example: Send a command to restart the PLC (adjust the register and function code as needed)
            # This is a hypothetical example, you need to know the specific register and function code for your PLC
            response = client.write_coil(0x0001, True)  # Example: Write to coil 0x0001 to trigger a restart
            
            if response.isError():
                print("Error: Failed to send restart command.")
            else:
                print("Restart command sent successfully.")
            
            # Close the connection
            client.close()
        else:
            print("Failed to connect to the PLC.")
    except Exception as e:
        print(f"Error: {e}")

# Main function
def main():
    # Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    
    if plc_ip:
        # Send the restart command to the PLC
        restart_plc(plc_ip)
    else:
        print("PLC not found. Cannot send restart command.")

if __name__ == "__main__":
    main()