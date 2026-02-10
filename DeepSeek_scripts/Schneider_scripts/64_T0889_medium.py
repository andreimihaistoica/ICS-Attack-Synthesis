from scapy.all import ARP, Ether, srp
from pymodbus.client.sync import ModbusTcpClient
import time

def discover_plc_ip():
    # Define the IP range to scan
    ip_range = "192.168.1.1/24"
    
    # Create an ARP request packet
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and receive the response
    result = srp(packet, timeout=2, verbose=0)[0]

    # Parse the response to find the PLC's IP address
    for sent, received in result:
        # Assuming the PLC's MAC address starts with a known prefix (e.g., 00:80:9F)
        if received.hwsrc.startswith("00:80:9F"):
            return received.psrc

    return None

def modify_plc_program(plc_ip):
    # Connect to the PLC using Modbus TCP
    client = ModbusTcpClient(plc_ip)
    client.connect()

    # Example: Modify a specific register or coil
    # This is a simplified example, actual program modification would require more complex logic
    # and possibly direct interaction with the PLC's programming environment.
    try:
        # Write to a holding register (address 0, value 1234)
        client.write_register(address=0, value=1234)
        print(f"Successfully modified register at address 0 on PLC {plc_ip}")
    except Exception as e:
        print(f"Failed to modify PLC program: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    # Step 1: Discover the PLC's IP address
    plc_ip = discover_plc_ip()
    
    if plc_ip:
        print(f"Discovered PLC at IP: {plc_ip}")
        
        # Step 2: Modify the PLC program
        modify_plc_program(plc_ip)
    else:
        print("Could not discover the PLC's IP address.")