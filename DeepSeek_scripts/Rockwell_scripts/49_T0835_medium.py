from scapy.all import ARP, Ether, srp
from pycomm3 import LogixDriver

def find_plc_ip():
    # Define the IP range to scan (adjust as needed)
    ip_range = "192.168.1.1/24"
    
    # Create an ARP request packet
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and receive the response
    result = srp(packet, timeout=2, verbose=0)[0]

    # Parse the response to find devices
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    # Assuming the PLC has a known MAC address prefix (e.g., Rockwell's prefix)
    plc_mac_prefix = "00:00:BC"
    for device in devices:
        if device['mac'].startswith(plc_mac_prefix):
            print(f"Found PLC at IP: {device['ip']}")
            return device['ip']

    print("PLC not found in the network.")
    return None

def manipulate_io_image(plc_ip):
    # Connect to the PLC
    with LogixDriver(plc_ip) as plc:
        # Example: Force an output coil to a desired status
        tag_name = "Output_Coil"  # Replace with the actual tag name
        desired_status = True  # True for ON, False for OFF

        # Write to the output coil
        plc.write(tag_name, desired_status)
        print(f"Output coil '{tag_name}' forced to {desired_status}.")

if __name__ == "__main__":
    plc_ip = find_plc_ip()
    if plc_ip:
        manipulate_io_image(plc_ip)