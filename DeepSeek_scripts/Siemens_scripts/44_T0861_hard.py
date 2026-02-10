import snap7
from snap7.util import *
from snap7.types import *
import socket

def find_plc_ip():
    # Broadcast a UDP packet to discover PLCs on the network
    # Note: This is a simple example and may need adjustments based on your network setup
    broadcast_address = '<broadcast>'  # Replace with your network's broadcast address
    port = 102  # Default Siemens S7 port

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(2.0)

    try:
        sock.sendto(b'discovery', (broadcast_address, port))
        data, addr = sock.recvfrom(1024)
        return addr[0]  # Return the IP address of the responding PLC
    except socket.timeout:
        print("PLC not found on the network.")
        return None
    finally:
        sock.close()

def collect_tags(plc_ip):
    # Create a PLC client
    plc = snap7.client.Client()
    plc.connect(plc_ip, 0, 1)

    # Define the tags and their memory addresses
    tags = {
        "Fan_A": {"type": "BOOL", "address": "Q0.0"},
        "Fan_B": {"type": "BOOL", "address": "Q0.1"},
        "Fan_A_Red": {"type": "BOOL", "address": "Q0.4"},
        "Fan_A_Green": {"type": "BOOL", "address": "Q0.5"},
        "Fan_B_Red": {"type": "BOOL", "address": "Q0.2"},
        "Fan_B_Green": {"type": "BOOL", "address": "Q0.3"},
        "Motor_Temp": {"type": "INT", "address": "MW7"},
        "Activate_Fan_A": {"type": "BOOL", "address": "M0.0"},
        "Activate_Fan_B": {"type": "BOOL", "address": "M0.1"},
        "Master_Fan_B_HMI": {"type": "BOOL", "address": "M0.5"},
        "Motor_Status": {"type": "BOOL", "address": "M0.7"},
        "Master_OFF": {"type": "BOOL", "address": "M0.6"},
        "Overheating_Check": {"type": "BOOL", "address": "M0.2"},
        "Tag_2": {"type": "BOOL", "address": "M0.4"},
    }

    # Collect and print tag values
    for tag_name, tag_info in tags.items():
        area = S7AreaDB if tag_info["address"].startswith("DB") else S7AreaMK if tag_info["address"].startswith("M") else S7AreaPE if tag_info["address"].startswith("I") else S7AreaPA
        start = int(tag_info["address"].split('.')[0][1:])
        bit = int(tag_info["address"].split('.')[1]) if '.' in tag_info["address"] else 0

        # Read the value from the PLC
        if tag_info["type"] == "BOOL":
            value = plc.read_area(area, 0, start, S7WLBit)
            value = get_bool(value, 0, bit)
        elif tag_info["type"] == "INT":
            value = plc.read_area(area, 0, start, S7WLWord)
            value = get_int(value, 0)

        print(f"{tag_name}: {value}")

    # Disconnect from the PLC
    plc.disconnect()

def main():
    # Find the PLC's IP address
    plc_ip = find_plc_ip()
    if not plc_ip:
        print("Could not find the PLC on the network.")
        return

    print(f"Found PLC at IP: {plc_ip}")

    # Collect and display tag values
    collect_tags(plc_ip)

if __name__ == "__main__":
    main()