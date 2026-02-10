import snap7
from scapy.all import ARP, Ether, srp

# Function to discover the PLC's IP address on the network
def discover_plc_ip(target_mac):
    # Create an ARP request packet
    arp = ARP(pdst="192.168.1.1/24")
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    # Send the packet and receive the response
    result = srp(packet, timeout=2, verbose=0)[0]

    # Parse the response to find the PLC's IP address
    for sent, received in result:
        if received.hwsrc.lower() == target_mac.lower():
            return received.psrc

    return None

# Function to modify alarm settings on the PLC
def modify_alarm_settings(plc_ip):
    # Initialize the S7 client
    client = snap7.client.Client()

    try:
        # Connect to the PLC
        client.connect(plc_ip, 0, 1)  # IP address, rack, slot

        # Example: Modify alarm settings by writing to a specific DB (Data Block)
        # Replace DB_NUMBER and OFFSET with the actual DB number and offset
        db_number = 10
        offset = 0
        new_alarm_setting = bytearray([0x00])  # Example: Disable alarm

        # Write the new alarm setting to the PLC
        client.db_write(db_number, offset, new_alarm_setting)

        print(f"Alarm settings modified successfully on PLC at {plc_ip}")

    except Exception as e:
        print(f"Error modifying alarm settings: {e}")

    finally:
        # Disconnect from the PLC
        client.disconnect()

# Main function
def main():
    # Replace with the PLC's MAC address
    plc_mac = "00:1C:06:XX:XX:XX"  # Replace with the actual MAC address

    # Discover the PLC's IP address
    plc_ip = discover_plc_ip(plc_mac)

    if plc_ip:
        print(f"Discovered PLC IP address: {plc_ip}")
        # Modify the alarm settings on the PLC
        modify_alarm_settings(plc_ip)
    else:
        print("PLC not found on the network.")

if __name__ == "__main__":
    main()