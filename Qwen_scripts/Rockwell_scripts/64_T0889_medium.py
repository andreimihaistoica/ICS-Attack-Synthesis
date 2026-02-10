import pycomm3
from pycomm3 import LogixDriver
from scapy.all import ARP, Ether, srp
import ipaddress

# Function to find the PLC's IP address
def find_plc_ip():
    # Define the target IP range to scan
    ip_range = "192.168.1.0/24"  # Change this to your network range
    # Create an ARP request packet
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp
    # Send the packet and capture the response
    result = srp(packet, timeout=2, verbose=False)[0]
    # Parse the response
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})
    # Filter the devices to find the PLC (assuming the PLC has a specific MAC address or other identifier)
    plc_ip = None
    for device in devices:
        if device['mac'] == '00:11:22:33:44:55':  # Change this to the PLC's MAC address
            plc_ip = device['ip']
            break
    return plc_ip

# Function to modify the PLC program
def modify_plc_program(plc_ip):
    try:
        # Connect to the PLC
        with LogixDriver(plc_ip) as plc:
            # Example: Add a new function to the PLC program
            new_function = """
            PROGRAM NewFunction
                // New function logic
                IF SomeCondition THEN
                    // Perform some action
                END_IF
            END_PROGRAM
            """
            # Upload the new function to the PLC
            plc.write('NewFunction', new_function)
            print("New function added to the PLC program.")
    except Exception as e:
        print(f"Error modifying PLC program: {e}")

# Main function
def main():
    # Find the PLC's IP address
    plc_ip = find_plc_ip()
    if plc_ip:
        print(f"PLC found at IP address: {plc_ip}")
        # Modify the PLC program
        modify_plc_program(plc_ip)
    else:
        print("PLC not found on the network.")

if __name__ == "__main__":
    main()