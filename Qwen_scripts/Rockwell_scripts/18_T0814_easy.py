from scapy.all import ARP, Ether, srp
import ipaddress

def find_plc_ip(target_subnet):
    # Create an ARP request packet
    arp = ARP(pdst=target_subnet)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    # Send the packet and capture the response
    result = srp(packet, timeout=2, verbose=False)[0]

    # Parse the response
    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    return devices

def main():
    # Define the target subnet (e.g., 192.168.1.0/24)
    target_subnet = "192.168.1.0/24"

    # Find devices on the network
    devices = find_plc_ip(target_subnet)

    # Print the list of devices
    print("Available devices in the network:")
    print("IP" + " "*18 + "MAC")
    for device in devices:
        print(f"{device['ip']}    {device['mac']}")

    # Identify the PLC (assuming you know the MAC address of the PLC)
    plc_mac = "00:11:22:33:44:55"  # Replace with the actual MAC address of the PLC
    plc_ip = None
    for device in devices:
        if device['mac'] == plc_mac:
            plc_ip = device['ip']
            break

    if plc_ip:
        print(f"PLC found at IP address: {plc_ip}")
    else:
        print("PLC not found in the network.")

if __name__ == "__main__":
    main()