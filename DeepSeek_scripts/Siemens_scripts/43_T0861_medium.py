import snap7
from scapy.all import ARP, Ether, srp
import pandas as pd

def discover_plc_ip(target_network="192.168.1.0/24"):
    """
    Discover the PLC's IP address using ARP scanning.
    Replace 'target_network' with your network's subnet.
    """
    print(f"Scanning network {target_network} for Siemens S7-1200 PLC...")
    arp = ARP(pdst=target_network)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether/arp

    result = srp(packet, timeout=2, verbose=0)[0]

    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    df = pd.DataFrame(devices)
    print("Discovered devices:")
    print(df)

    # Assuming the Siemens S7-1200 has a specific MAC prefix
    plc_ip = None
    for device in devices:
        if device['mac'].startswith("08:00:06"):  # Siemens MAC prefix
            plc_ip = device['ip']
            print(f"Found Siemens S7-1200 PLC at IP: {plc_ip}")
            break

    if not plc_ip:
        print("Siemens S7-1200 PLC not found on the network.")
        exit(1)

    return plc_ip

def read_plc_tags(plc_ip, rack=0, slot=1):
    """
    Read tags/points from the Siemens S7-1200 PLC.
    """
    # Connect to the PLC
    plc = snap7.client.Client()
    plc.connect(plc_ip, rack, slot)

    if plc.get_connected():
        print(f"Connected to PLC at {plc_ip}")

        # Example: Read DB1 (Data Block 1) from byte 0 to 10
        db_number = 1
        start_address = 0
        size = 10
        data = plc.db_read(db_number, start_address, size)

        print(f"Data read from DB{db_number}: {data}")

        # Disconnect from the PLC
        plc.disconnect()
        print("Disconnected from PLC.")
    else:
        print("Failed to connect to the PLC.")

def main():
    # Step 1: Discover the PLC's IP address
    plc_ip = discover_plc_ip()

    # Step 2: Read tags/points from the PLC
    read_plc_tags(plc_ip)

if __name__ == "__main__":
    main()